"""split.py — build chat-format training data and split train/heldout.

Reads data/out/enriched.jsonl (one row per workflow x natural-language prompt,
see enrich.py) and builds chat-format examples:
  system    -> the FIXED FlowForge system prompt (must match backend/app/prompts.py)
  user      -> the natural request (row["description"])
  assistant -> the workflow JSON, minified (no extra whitespace)

Split 85/15 by TEMPLATE ID (not by row), so every rewrite of the same workflow
lands in the same split — no leakage between train and heldout.

Output: data/out/train.jsonl and data/out/heldout.jsonl, each line:
    {"messages": [{"role": "system", ...}, {"role": "user", ...}, {"role": "assistant", ...}]}

Usage:
    python data/split.py
    python data/split.py --seed 7 --train-fraction 0.85
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

ENRICHED_IN = Path(__file__).resolve().parent / "out" / "enriched.jsonl"
TRAIN_OUT = Path(__file__).resolve().parent / "out" / "train.jsonl"
HELDOUT_OUT = Path(__file__).resolve().parent / "out" / "heldout.jsonl"

TRAIN_FRACTION = 0.85
DEFAULT_SEED = 42

# Keep identical to backend/app/prompts.py SYSTEM_PROMPT.
SYSTEM_PROMPT = (
    "You are FlowForge, an expert n8n workflow generator. Given a natural "
    "language description of an automation, return ONLY valid n8n workflow "
    "JSON with a nodes array and connections object. Do not include sticky "
    "notes, explanations, markdown, or any text outside the JSON."
)


def load_enriched(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"No input file at {path} — run data/enrich.py first.")
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def to_chat_example(row: dict) -> dict:
    assistant_json = json.dumps(row["workflow"], ensure_ascii=False, separators=(",", ":"))
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": row["description"]},
            {"role": "assistant", "content": assistant_json},
        ]
    }


def split_ids(template_ids: list[str], train_fraction: float, seed: int) -> tuple[set[str], set[str]]:
    """Deterministic shuffle-then-slice split of template ids (not rows)."""
    ids = sorted(template_ids)  # sort first so the shuffle is reproducible regardless of input order
    random.Random(seed).shuffle(ids)
    cutoff = int(len(ids) * train_fraction)
    return set(ids[:cutoff]), set(ids[cutoff:])


def log_stats(train_examples: list[dict], heldout_examples: list[dict]) -> None:
    def lengths(examples: list[dict]) -> list[int]:
        return [sum(len(m["content"]) for m in ex["messages"]) for ex in examples]

    all_lengths = lengths(train_examples) + lengths(heldout_examples)
    total = len(all_lengths)

    print("\n=== split.py stats ===")
    print(f"Total examples: {total}")
    print(f"Train:          {len(train_examples)}")
    print(f"Heldout:        {len(heldout_examples)}")

    if all_lengths:
        avg_len = sum(all_lengths) / total
        max_len = max(all_lengths)
        print(f"Avg example length: {avg_len:.0f} chars (~{avg_len / 4:.0f} tokens estimated)")
        print(f"Max example length: {max_len} chars (~{max_len / 4:.0f} tokens estimated)")


def split(train_fraction: float, seed: int) -> None:
    rows = load_enriched(ENRICHED_IN)
    if not rows:
        print("No enriched rows found — nothing to split.")
        return

    template_ids = list({r["template_id"] for r in rows})
    train_ids, heldout_ids = split_ids(template_ids, train_fraction, seed)

    train_examples = [to_chat_example(r) for r in rows if r["template_id"] in train_ids]
    heldout_examples = [to_chat_example(r) for r in rows if r["template_id"] in heldout_ids]

    TRAIN_OUT.parent.mkdir(parents=True, exist_ok=True)
    with TRAIN_OUT.open("w", encoding="utf-8") as f:
        for ex in train_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    with HELDOUT_OUT.open("w", encoding="utf-8") as f:
        for ex in heldout_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    print(f"Templates: {len(template_ids)} total -> {len(train_ids)} train / {len(heldout_ids)} heldout")
    log_stats(train_examples, heldout_examples)


def main() -> None:
    parser = argparse.ArgumentParser(description="Split enriched data into train/heldout chat-format examples.")
    parser.add_argument("--train-fraction", type=float, default=TRAIN_FRACTION)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args()
    split(train_fraction=args.train_fraction, seed=args.seed)


if __name__ == "__main__":
    main()
