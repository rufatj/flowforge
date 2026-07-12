"""Local-inference eval matching finetune_plain.py exactly: same tokenizer
call shape, same prefix method, generation settings sized for this failure
mode (see docs — 21% of real answers exceed 4096 tokens; greedy-only
decoding on structured JSON needs a repetition guard once near the cap).

Usage (from /workspace/flowforge on the pod):
    python3 eval/local_eval_plain.py --model unsloth/gemma-3-4b-it \
        --label base-gemma-3-4b --limit 30 --out /workspace/eval_base.json
    python3 eval/local_eval_plain.py --model ml/outputs/merged-gemma-flowforge \
        --label fine-tuned --limit 30 --out /workspace/eval_ft.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from eval.harness import run_gates
from eval.json_extract import extract_json

HELDOUT = Path(__file__).resolve().parents[1] / "data" / "out" / "heldout.jsonl"


def _ids(x):
    if hasattr(x, "input_ids"):
        x = x.input_ids
    if isinstance(x, dict):
        x = x["input_ids"]
    if x and isinstance(x[0], list):
        x = x[0]
    if hasattr(x, "ids"):
        x = x.ids
    return list(x)


def load_prompts(limit):
    rows = []
    with HELDOUT.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line)["messages"][:2])  # [system, user]
            if limit and len(rows) >= limit:
                break
    return rows


def load_model(path):
    import torch
    import transformers
    last = None
    for cls_name in ("AutoModelForCausalLM", "AutoModelForImageTextToText"):
        try:
            cls = getattr(transformers, cls_name)
            m = cls.from_pretrained(path, torch_dtype=torch.bfloat16, device_map="auto")
            print(f"[eval] loaded {path} via {cls_name}", flush=True)
            return m
        except Exception as e:
            print(f"[eval] {cls_name} failed: {str(e)[:200]}", flush=True)
            last = e
    raise last


def stop_when_json_closes(text: str) -> bool:
    """True once a balanced top-level {...} has appeared — lets us stop early."""
    return extract_json(text) is not None


def generate_one(model, tok, msgs, max_new_tokens):
    import torch
    ids = _ids(tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=True))
    inputs = torch.tensor([ids]).to(model.device)
    # Simple chunked generation with an early stop the instant valid JSON closes —
    # avoids paying for the full max_new_tokens budget on every example while still
    # allowing the full budget for examples that legitimately need it.
    chunk = 512
    generated = inputs
    text = ""
    for _ in range(0, max_new_tokens, chunk):
        with torch.no_grad():
            out = model.generate(
                input_ids=generated, max_new_tokens=chunk, do_sample=False,
                repetition_penalty=1.1, no_repeat_ngram_size=6,
                eos_token_id=[1, 106],  # <eos> and <end_of_turn>
                pad_token_id=tok.pad_token_id or tok.eos_token_id,
            )
        new_text = tok.decode(out[0][generated.shape[1]:], skip_special_tokens=True)
        text += new_text
        generated = out
        if stop_when_json_closes(text) or out.shape[1] - inputs.shape[1] >= max_new_tokens:
            break
        if new_text == "":  # generation ended (EOS) before closing valid JSON
            break
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--limit", type=int, default=30)
    ap.add_argument("--max-new-tokens", type=int, default=6144)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(a.model)
    model = load_model(a.model)
    model.eval()
    prompts = load_prompts(a.limit)
    print(f"[eval] {a.label}: {len(prompts)} heldout prompts, max_new_tokens={a.max_new_tokens}", flush=True)

    g1 = g2 = 0
    examples = []
    for i, msgs in enumerate(prompts, 1):
        text = generate_one(model, tok, msgs, a.max_new_tokens)
        r = run_gates(text, live_import=False)
        g1 += r.json_valid
        g2 += r.schema_valid
        print(f"  [{i}/{len(prompts)}] json={r.json_valid} schema={r.schema_valid} len={len(text)}", flush=True)
        if len(examples) < 5:
            examples.append({"prompt": msgs[1]["content"][:200], "output": text[:1000], "gates": r.as_dict()})

    n = len(prompts)
    res = {"label": a.label, "model": a.model, "total": n,
           "gate1": round(g1 / n, 4) if n else 0.0,
           "gate2": round(g2 / n, 4) if n else 0.0,
           "gate3": None, "examples": examples}
    Path(a.out).write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[eval] {a.label}: gate1={res['gate1']:.1%} gate2={res['gate2']:.1%} -> {a.out}", flush=True)


if __name__ == "__main__":
    main()
