"""collect_hf.py — fast fallback dataset source: mbakgun/n8nbuilder-n8n-workflows-dataset.

If api.n8n.io is slow, rate-limited, or its schema shifts mid-hackathon, this
script pulls a ready-made, pre-curated set of 2,737 n8n workflow templates from
Hugging Face and converts it into the exact same data/out/raw_templates.jsonl
format that collect.py writes, so clean.py/enrich.py/split.py don't care which
source a record came from.

Dataset shape (verified live on 2026-07-07): the repo ships two files with
DIFFERENT schemas (loading the dataset without data_files= fails with a
DatasetGenerationCastError because the loader tries to merge both):
  - train.jsonl        -> {"instruction", "input", "output"}  (Alpaca format)
  - train_openai.jsonl -> {"messages": [...]}                 (OpenAI chat format)
Both encode the SAME underlying 2,737 templates in different wrappers, so we
only load train.jsonl. `output` is a JSON STRING of the full raw n8n workflow
export: {"id", "meta", "name", "tags", "nodes", "active", "settings",
"versionId", "connections"} — we keep only nodes/connections, matching the
`workflow` shape collect.py writes. `input` is the template's natural-language
description (richer than n8n's own template blurbs) — used as `description`.

Usage:
    python data/collect_hf.py --limit 5     # smoke test
    python data/collect_hf.py               # full 2,737 templates

Dedup: shares data/out/raw_templates.jsonl and its id-based resume logic with
collect.py (imported directly, since both live in this folder). HF records are
id-prefixed "hf-" so they can never collide with api.n8n.io's numeric ids.
"""
from __future__ import annotations

import argparse
import json
import sys

from datasets import load_dataset

from collect import RAW_OUT, load_existing_ids, log_stats

HF_DATASET = "mbakgun/n8nbuilder-n8n-workflows-dataset"
HF_DATA_FILE = "train.jsonl"


def collect_hf(limit: int | None) -> None:
    RAW_OUT.parent.mkdir(parents=True, exist_ok=True)
    seen_ids = load_existing_ids()
    print(f"Resuming: {len(seen_ids)} templates already collected (all sources).")

    print(f"Loading {HF_DATASET} ({HF_DATA_FILE}) from Hugging Face...")
    rows = load_dataset(HF_DATASET, data_files=HF_DATA_FILE, split="train")
    print(f"Loaded {len(rows)} rows.")

    new_count = 0
    with RAW_OUT.open("a", encoding="utf-8") as out_f:
        for row in rows:
            if limit is not None and new_count >= limit:
                break

            try:
                wf = json.loads(row["output"])
            except (json.JSONDecodeError, TypeError):
                print("  skip row: output is not valid JSON", file=sys.stderr)
                continue

            raw_id = wf.get("id")
            template_id = f"hf-{raw_id}" if raw_id else f"hf-hash-{hash(row['output']) & 0xFFFFFFFF}"
            if template_id in seen_ids:
                continue

            nodes = wf.get("nodes") or []
            connections = wf.get("connections") or {}
            if not nodes:
                print(f"  skip {template_id}: zero nodes", file=sys.stderr)
                continue

            node_types = sorted({n["type"] for n in nodes if "type" in n})
            record = {
                "source": "hf",
                "id": template_id,
                "name": wf.get("name") or "",
                "description": row.get("input") or "",
                "workflow": {"nodes": nodes, "connections": connections},
                "node_types": node_types,
                "node_count": len(nodes),
            }
            out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
            out_f.flush()
            seen_ids.add(template_id)
            new_count += 1

            if new_count % 100 == 0:
                print(f"  collected {new_count} new templates so far...")

    print(f"Done. {new_count} new templates collected this run.")
    log_stats()


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect n8n templates from the HF fallback dataset.")
    parser.add_argument("--limit", type=int, default=None, help="Max NEW templates to add this run.")
    args = parser.parse_args()
    collect_hf(limit=args.limit)


if __name__ == "__main__":
    main()
