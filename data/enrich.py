"""enrich.py — turn template descriptions into natural, user-style prompts.

Many n8n template descriptions are terse or written for other automation
builders ("Webhook to Google Sheets"), not how a real person would ask for the
automation in plain language. For each clean workflow, this calls an
OpenAI-compatible model (Fireworks by default; FIREWORKS_API_KEY,
FIREWORKS_MODEL, and optionally FIREWORKS_BASE_URL from env) to write 2
natural-language rewrites, given the workflow's node list and original
description as context.

Each workflow yields up to 3 training examples in the output: the ORIGINAL
description (always kept, so a total enrichment failure still leaves the
workflow usable) plus up to 2 LLM rewrites — matching "1 workflow becomes 2-3
training examples" depending on how many rewrites succeed.

Output: data/out/enriched.jsonl, one row per (workflow, prompt) pair:
    {"template_id", "source", "prompt_source": "original"|"rewrite_1"|"rewrite_2",
     "description": "<the NL prompt to train on>",
     "workflow": {...}, "node_types": [...], "node_count": int}

Resume: any template_id already present in enriched.jsonl (from a prior run,
successful or not) is skipped entirely — delete its rows to force a redo.

Usage:
    python data/enrich.py --limit 10          # ALWAYS do this first
    python data/enrich.py --concurrency 8 --batch-size 20
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

# find_dotenv() walks up from this file's own directory, so this finds
# flowforge/.env regardless of the process's working directory or shell.
load_dotenv()

CLEAN_IN = Path(__file__).resolve().parent / "out" / "clean.jsonl"
ENRICHED_OUT = Path(__file__).resolve().parent / "out" / "enriched.jsonl"

FIREWORKS_API_KEY = os.environ.get("FIREWORKS_API_KEY", "")
FIREWORKS_MODEL = os.environ.get("FIREWORKS_MODEL", "accounts/fireworks/models/gemma-3-12b-it")
FIREWORKS_BASE_URL = os.environ.get("FIREWORKS_BASE_URL", "https://api.fireworks.ai/inference/v1")

REWRITES_PER_WORKFLOW = 2
MAX_RETRIES = 3

_PREFIX_STRIP = ("n8n-nodes-base.", "@n8n/n8n-nodes-langchain.")


def _friendly_label(node_type: str) -> str:
    """"n8n-nodes-base.httpRequest" -> "Http Request" (a readable hint for the LLM)."""
    label = node_type
    for prefix in _PREFIX_STRIP:
        if label.startswith(prefix):
            label = label[len(prefix):]
            break
    label = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", label)
    return label[:1].upper() + label[1:] if label else label


def build_prompt(record: dict) -> str:
    node_labels = ", ".join(_friendly_label(t) for t in record["node_types"]) or "unknown nodes"
    return (
        f"Workflow name: {record['name']}\n"
        f"Nodes used: {node_labels}\n"
        f"Original description: {record['description']}\n\n"
        "Write 2 different natural-language requests that a real, non-technical "
        "n8n user might type to ask for this exact automation to be built. Plain "
        "conversational English, one or two sentences each. Describe the RESULT "
        "the user wants; do not mention node names or technical implementation "
        "details.\n\n"
        'Return ONLY a JSON array of exactly 2 strings, nothing else. '
        'Example: ["...", "..."]'
    )


def _parse_rewrites(content: str) -> list[str]:
    """Parse the model's JSON-array response. Tolerates markdown code fences."""
    text = content.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    parsed = json.loads(text)
    if not isinstance(parsed, list):
        raise ValueError("response is not a JSON array")
    rewrites = [r.strip() for r in parsed if isinstance(r, str) and r.strip()]
    return rewrites[:REWRITES_PER_WORKFLOW]


class Enricher:
    """Wraps the OpenAI-compatible client + running token/cost totals."""

    def __init__(self, api_key: str, base_url: str, model: str) -> None:
        self.client = OpenAI(api_key=api_key or "EMPTY", base_url=base_url)
        self.model = model
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.api_calls = 0
        self.failures = 0

    def get_rewrites(self, record: dict) -> list[str]:
        """Call the model for up to MAX_RETRIES attempts; return [] on total failure."""
        user_prompt = build_prompt(record)
        last_error: Exception | None = None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                messages = [{"role": "user", "content": user_prompt}]
                if attempt > 1:
                    messages.append(
                        {
                            "role": "user",
                            "content": "Reminder: reply with ONLY a JSON array of 2 strings, no other text.",
                        }
                    )
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=400,
                )
                self.api_calls += 1
                if resp.usage:
                    self.prompt_tokens += resp.usage.prompt_tokens or 0
                    self.completion_tokens += resp.usage.completion_tokens or 0
                content = resp.choices[0].message.content or ""
                return _parse_rewrites(content)
            except Exception as e:  # noqa: BLE001 - genuinely any failure should retry/skip, not crash the run
                last_error = e
                time.sleep(1.5 * attempt)

        self.failures += 1
        print(f"  enrich failed for {record['id']} after {MAX_RETRIES} attempts: {last_error}", file=sys.stderr)
        return []


def load_clean_records(path: Path) -> list[dict]:
    if not path.exists():
        print(f"No input file at {path} — run data/clean.py first.", file=sys.stderr)
        return []
    records = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def load_done_template_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    ids: set[str] = set()
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                ids.add(json.loads(line)["template_id"])
            except (json.JSONDecodeError, KeyError):
                continue
    return ids


def rows_for_record(record: dict, rewrites: list[str]) -> list[dict]:
    """Original description + up to 2 rewrites, all pointing at the same workflow."""
    base = {
        "template_id": record["id"],
        "source": record["source"],
        "workflow": record["workflow"],
        "node_types": record["node_types"],
        "node_count": record["node_count"],
    }
    rows = [{**base, "prompt_source": "original", "description": record["description"]}]
    for i, rewrite in enumerate(rewrites, start=1):
        rows.append({**base, "prompt_source": f"rewrite_{i}", "description": rewrite})
    return rows


def enrich(limit: int | None, batch_size: int, concurrency: int) -> None:
    if not FIREWORKS_API_KEY:
        print("WARNING: FIREWORKS_API_KEY is not set; requests will likely fail.", file=sys.stderr)

    ENRICHED_OUT.parent.mkdir(parents=True, exist_ok=True)
    all_records = load_clean_records(CLEAN_IN)
    done_ids = load_done_template_ids(ENRICHED_OUT)
    print(f"Loaded {len(all_records)} clean records. {len(done_ids)} template ids already enriched (skipping).")

    todo = [r for r in all_records if r["id"] not in done_ids]
    if limit is not None:
        todo = todo[:limit]
    print(f"Enriching {len(todo)} templates this run (batch_size={batch_size}, concurrency={concurrency}).")

    enricher = Enricher(FIREWORKS_API_KEY, FIREWORKS_BASE_URL, FIREWORKS_MODEL)
    total_rows_written = 0
    templates_processed = 0

    with ENRICHED_OUT.open("a", encoding="utf-8") as out_f:
        for batch_start in range(0, len(todo), batch_size):
            batch = todo[batch_start : batch_start + batch_size]
            with ThreadPoolExecutor(max_workers=concurrency) as pool:
                future_to_record = {pool.submit(enricher.get_rewrites, r): r for r in batch}
                for future in as_completed(future_to_record):
                    record = future_to_record[future]
                    rewrites = future.result()
                    rows = rows_for_record(record, rewrites)
                    for row in rows:
                        out_f.write(json.dumps(row, ensure_ascii=False) + "\n")
                    total_rows_written += len(rows)
                    templates_processed += 1
            out_f.flush()
            print(
                f"  batch done: {templates_processed}/{len(todo)} templates, "
                f"{total_rows_written} rows written so far"
            )

    print(f"\nDone. {templates_processed} templates processed, {total_rows_written} training rows written.")
    print(
        f"API calls: {enricher.api_calls}  failures: {enricher.failures}  "
        f"prompt_tokens: {enricher.prompt_tokens}  completion_tokens: {enricher.completion_tokens}  "
        f"total_tokens: {enricher.prompt_tokens + enricher.completion_tokens}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Enrich clean workflows with natural-language prompt rewrites.")
    parser.add_argument("--limit", type=int, default=None, help="Max NEW templates to process this run.")
    parser.add_argument("--batch-size", type=int, default=20, help="Templates per flush-to-disk batch.")
    parser.add_argument("--concurrency", type=int, default=5, help="Parallel API requests.")
    args = parser.parse_args()
    enrich(limit=args.limit, batch_size=args.batch_size, concurrency=args.concurrency)


if __name__ == "__main__":
    main()
