"""Load data/out/train.jsonl (chat format) for SFT.

Each line is {"messages": [{role, content} x3]} as written by data/split.py.
We render each conversation to a single training string with the tokenizer's
own chat template, so the model is trained on exactly the token layout it
will see at inference time behind the OpenAI-compatible endpoint.
"""
from __future__ import annotations

import json
from pathlib import Path

from datasets import Dataset

REPO_ROOT = Path(__file__).resolve().parents[1]
TRAIN_FILE = REPO_ROOT / "data" / "out" / "train.jsonl"
HELDOUT_FILE = REPO_ROOT / "data" / "out" / "heldout.jsonl"


def load_chat_rows(path: Path = TRAIN_FILE) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"{path} not found - run the data pipeline first (enrich.py, split.py).")
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    if not rows:
        raise ValueError(f"{path} is empty.")
    return rows


def build_dataset(tokenizer, path: Path = TRAIN_FILE) -> Dataset:
    """Return a Dataset with a 'text' column rendered via the chat template."""
    rows = load_chat_rows(path)

    def render(row: dict) -> dict:
        return {
            "text": tokenizer.apply_chat_template(
                row["messages"], tokenize=False, add_generation_prompt=False
            )
        }

    dataset = Dataset.from_list(rows)
    return dataset.map(render, remove_columns=dataset.column_names, desc="chat-templating")


def heldout_prompts(n: int = 3) -> list[str]:
    """First N user prompts from the heldout set, for the post-train smoke test."""
    rows = load_chat_rows(HELDOUT_FILE)[:n]
    return [next(m["content"] for m in r["messages"] if m["role"] == "user") for r in rows]
