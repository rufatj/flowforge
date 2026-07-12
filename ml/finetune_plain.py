"""Plain transformers.Trainer + PEFT LoRA SFT — gemma-3-4b-it on W7900 (gfx1100).

Unsloth segfaults on RDNA3 and Gemma-4-E4B is PEFT-incompatible, so this is the
no-magic path: HF Trainer + LoRA. Every known failure mode from runs 1-2 is
addressed and ASSERTED here, not assumed:

  R1 lesson: never truncate mid-JSON  -> examples longer than MAX_LEN are DROPPED.
  R2 lesson: masking boundary         -> two-template method, verified token-by-token
             (p_ids IS an exact prefix of f_ids for Gemma-3 on 200/200 sampled rows),
             plus a HARD per-example assert so any surprise fails fast, before GPU hours.
  EOS       : sequence is cut exactly after the final <end_of_turn> (the template
              appends a trailing '\n' after it — stripped), so EOS is the last
              supervised token of every example.

Run (inside the pod venv, from /workspace/flowforge):
    python3 -m ml.finetune_plain
Resumes automatically from ml/outputs/checkpoints-plain/checkpoint-* if present.
"""
from __future__ import annotations

import glob
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

MODEL_ID = os.environ.get("FLOWFORGE_BASE_MODEL", "unsloth/gemma-3-4b-it")
TRAIN_FILE = REPO / "data" / "out" / "train.jsonl"
HELDOUT_FILE = REPO / "data" / "out" / "heldout.jsonl"
OUT_DIR = REPO / "ml" / "outputs"
CKPT_DIR = OUT_DIR / "checkpoints-plain"
ADAPTER_DIR = OUT_DIR / "lora_adapter"
MERGED_DIR = OUT_DIR / "merged-gemma-flowforge"

MAX_LEN = 6144          # drop (never truncate) beyond this
EPOCHS = 1
LR = 2e-4
BATCH = 1               # per device; no padding waste at batch 1
GRAD_ACCUM = 16         # effective batch 16
LORA_R, LORA_ALPHA = 16, 32
TARGET_MODULES = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]


def _ids(x):
    """Normalize transformers 4.x/5.x apply_chat_template return types to list[int]."""
    if hasattr(x, "input_ids"):
        x = x.input_ids
    if isinstance(x, dict):
        x = x["input_ids"]
    if x and isinstance(x[0], list):
        x = x[0]
    if hasattr(x, "ids"):
        x = x.ids
    return list(x)


def load_model(model_id):
    import torch
    import transformers
    last = None
    for cls_name in ("AutoModelForCausalLM", "AutoModelForImageTextToText"):
        try:
            cls = getattr(transformers, cls_name)
            m = cls.from_pretrained(model_id, torch_dtype=torch.bfloat16, device_map="auto",
                                    attn_implementation="eager")  # safest on RDNA3
            print(f"[model] loaded {model_id} via {cls_name}", flush=True)
            return m
        except Exception as e:
            print(f"[model] {cls_name} failed: {str(e)[:200]}", flush=True)
            last = e
    raise last


def build_examples(tok):
    """Tokenize with prompt-masked labels; EOS (<end_of_turn>) is the final supervised token."""
    eot = tok.convert_tokens_to_ids("<end_of_turn>")
    kept, dropped, examples = 0, 0, []
    with TRAIN_FILE.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            msgs = json.loads(line)["messages"]
            p = _ids(tok.apply_chat_template(msgs[:2], add_generation_prompt=True, tokenize=True))
            full = _ids(tok.apply_chat_template(msgs, add_generation_prompt=False, tokenize=True))
            # HARD boundary check — verified sound for Gemma-3, asserted anyway.
            if full[: len(p)] != p:
                raise AssertionError(
                    "prompt render is NOT a token prefix of full render — masking would "
                    f"be misaligned. Offending prompt: {msgs[1]['content'][:120]!r}")
            assert eot in full, "no <end_of_turn> in rendered conversation"
            last_eot = len(full) - 1 - full[::-1].index(eot)
            full = full[: last_eot + 1]           # strip trailing '\n' after final EOS
            if len(full) > MAX_LEN:
                dropped += 1
                continue
            labels = [-100] * len(p) + full[len(p):]
            assert len(labels) == len(full) and labels[-1] == eot
            examples.append({"input_ids": full, "labels": labels})
            kept += 1
    print(f"[data] kept {kept}, dropped {dropped} (> {MAX_LEN} tokens)", flush=True)
    return examples


class ListDataset:
    def __init__(self, rows): self.rows = rows
    def __len__(self): return len(self.rows)
    def __getitem__(self, i): return self.rows[i]


class Collator:
    """Pad input_ids with pad_id, labels with -100 (irrelevant at batch 1, correct anyway)."""
    def __init__(self, pad_id): self.pad_id = pad_id
    def __call__(self, feats):
        import torch
        width = max(len(x["input_ids"]) for x in feats)
        batch = {"input_ids": [], "attention_mask": [], "labels": []}
        for x in feats:
            n = len(x["input_ids"])
            batch["input_ids"].append(x["input_ids"] + [self.pad_id] * (width - n))
            batch["attention_mask"].append([1] * n + [0] * (width - n))
            batch["labels"].append(x["labels"] + [-100] * (width - n))
        return {k: torch.tensor(v) for k, v in batch.items()}


def canary(model, tok, n=2):
    """Greedy-generate a couple of heldout prompts right after training."""
    import torch
    rows = []
    with HELDOUT_FILE.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line)["messages"][:2])
            if len(rows) >= n:
                break
    for msgs in rows:
        ids = _ids(tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=True))
        inputs = torch.tensor([ids]).to(model.device)
        out = model.generate(input_ids=inputs, max_new_tokens=600, do_sample=False,
                             repetition_penalty=1.05, eos_token_id=[1, 106])
        text = tok.decode(out[0][inputs.shape[1]:], skip_special_tokens=True)
        print(f"\n[canary] {msgs[1]['content'][:80]!r}\n{text[:400]}\n", flush=True)


def main():
    from peft import LoraConfig, get_peft_model
    from transformers import AutoTokenizer, Trainer, TrainingArguments

    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    examples = build_examples(tok)

    model = load_model(MODEL_ID)
    model.config.use_cache = False
    if hasattr(model, "enable_input_require_grads"):
        model.enable_input_require_grads()      # needed for checkpointing + frozen base
    lora = LoraConfig(r=LORA_R, lora_alpha=LORA_ALPHA, lora_dropout=0.0,
                      target_modules=TARGET_MODULES, task_type="CAUSAL_LM")
    model = get_peft_model(model, lora)
    model.print_trainable_parameters()

    args = TrainingArguments(
        output_dir=str(CKPT_DIR),
        num_train_epochs=EPOCHS,
        learning_rate=LR,
        lr_scheduler_type="cosine",
        warmup_ratio=0.03,
        per_device_train_batch_size=BATCH,
        gradient_accumulation_steps=GRAD_ACCUM,
        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
        bf16=True,
        optim="adamw_torch",
        weight_decay=0.01,
        logging_steps=10,
        save_strategy="steps", save_steps=50, save_total_limit=2,
        report_to="none",
        seed=42,
    )
    pad_id = tok.pad_token_id if tok.pad_token_id is not None else 0
    trainer = Trainer(model=model, args=args, train_dataset=ListDataset(examples),
                      data_collator=Collator(pad_id))

    ckpts = glob.glob(str(CKPT_DIR / "checkpoint-*"))
    print(f"[resume] found {len(ckpts)} checkpoint(s)", flush=True)
    trainer.train(resume_from_checkpoint=True if ckpts else None)

    ADAPTER_DIR.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(str(ADAPTER_DIR))
    tok.save_pretrained(str(ADAPTER_DIR))
    print(f"[save] LoRA adapter -> {ADAPTER_DIR}", flush=True)

    merged = model.merge_and_unload()
    MERGED_DIR.mkdir(parents=True, exist_ok=True)
    merged.save_pretrained(str(MERGED_DIR))
    tok.save_pretrained(str(MERGED_DIR))
    print(f"[save] merged bf16 -> {MERGED_DIR}", flush=True)

    merged.config.use_cache = True
    canary(merged, tok)


if __name__ == "__main__":
    main()
