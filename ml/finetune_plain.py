import os, glob, torch
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import Dataset
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from peft import LoraConfig, get_peft_model

MODEL_ID   = os.environ.get("MODEL_ID", "unsloth/gemma-3-4b-it")
MERGED_DIR = os.environ.get("MERGED_DIR", "/workspace/flowforge/ml/outputs/merged-gemma-flowforge")
CKPT_DIR   = "/workspace/flowforge/ml/outputs/checkpoints"
DATA       = "/workspace/flowforge/data/out/train.jsonl"

MAX_LEN = 6144

print(f"[ft] loading {MODEL_ID}", flush=True)
tok = AutoTokenizer.from_pretrained(MODEL_ID)
if tok.pad_token is None:
    tok.pad_token = tok.eos_token
EOS = tok.eos_token_id
print(f"[ft] eos_token={tok.eos_token!r} id={EOS}", flush=True)

model = AutoModelForCausalLM.from_pretrained(MODEL_ID, dtype=torch.bfloat16, device_map="auto")
model.gradient_checkpointing_enable()
model.config.use_cache = False

lora_cfg = LoraConfig(
    r=16, lora_alpha=32, lora_dropout=0.0,
    target_modules=["q_proj","k_proj","v_proj","o_proj","gate_proj","up_proj","down_proj"],
    task_type="CAUSAL_LM",
)
model = get_peft_model(model, lora_cfg)
model.print_trainable_parameters()

raw = load_dataset("json", data_files=DATA, split="train")

class ChatDataset(Dataset):
    def __init__(self, raw_ds):
        self.rows = []
        skipped = 0
        for ex in raw_ds:
            msgs = ex["messages"]
            answer = [m for m in msgs if m["role"] == "assistant"]
            prompt = [m for m in msgs if m["role"] != "assistant"]
            if not answer:
                skipped += 1
                continue

            p_text = tok.apply_chat_template(prompt, tokenize=False, add_generation_prompt=True)
            full_text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=False)

            p_ids = tok(p_text, add_special_tokens=False)["input_ids"]
            f_ids = tok(full_text, add_special_tokens=False)["input_ids"]

            while f_ids and f_ids[-1] != EOS:
                f_ids.pop()
            if not f_ids:
                skipped += 1
                continue

            if len(f_ids) > MAX_LEN:
                skipped += 1
                continue
            if len(p_ids) >= len(f_ids):
                skipped += 1
                continue

            labels = [-100] * len(p_ids) + f_ids[len(p_ids):]
            self.rows.append((f_ids, labels))

        print(f"[ft] kept {len(self.rows)} examples, skipped {skipped}", flush=True)
        assert self.rows, "no usable training examples!"

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, i):
        ids, labels = self.rows[i]
        return {"input_ids": ids, "labels": labels}

print("[ft] tokenizing...", flush=True)
ds = ChatDataset(raw)

def collate(batch):
    input_ids = [torch.tensor(b["input_ids"], dtype=torch.long) for b in batch]
    labels    = [torch.tensor(b["labels"],    dtype=torch.long) for b in batch]
    input_ids = pad_sequence(input_ids, batch_first=True, padding_value=tok.pad_token_id)
    labels    = pad_sequence(labels,    batch_first=True, padding_value=-100)
    attention_mask = (input_ids != tok.pad_token_id).long()
    token_type_ids = torch.zeros_like(input_ids)
    return {"input_ids": input_ids, "attention_mask": attention_mask,
            "labels": labels, "token_type_ids": token_type_ids}

ckpts = glob.glob(f"{CKPT_DIR}/checkpoint-*")
resume = True if ckpts else None
print(f"[ft] checkpoints found: {len(ckpts)}, resume={resume}", flush=True)

args = TrainingArguments(
    output_dir=CKPT_DIR,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=16,
    num_train_epochs=1,
    learning_rate=2e-4,
    logging_steps=10,
    save_strategy="steps",
    save_steps=50,
    save_total_limit=2,
    bf16=True,
    optim="adamw_torch",
    report_to=[],
)

trainer = Trainer(model=model, args=args, train_dataset=ds, data_collator=collate)
trainer.train(resume_from_checkpoint=resume)
assert trainer.state.global_step > 0, "training ran zero steps!"

print(f"[ft] done ({trainer.state.global_step} steps), merging -> {MERGED_DIR}", flush=True)
merged = model.merge_and_unload()
os.makedirs(MERGED_DIR, exist_ok=True)
merged.save_pretrained(MERGED_DIR)
tok.save_pretrained(MERGED_DIR)
print("[ft] DONE", flush=True)