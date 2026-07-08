"""quality_check.py — sanity-check ground-truth heldout examples against the gate cascade.

Takes N random rows straight from data/out/heldout.jsonl (the ASSISTANT
ground-truth JSON, not any model output) and runs them through eval.harness's
three gates. This confirms the training targets themselves are clean and
importable, independent of any model. No Fireworks/model calls are made.

Usage:
    python -m eval.quality_check --n 30 --seed 0
    python -m eval.quality_check --n 30 --no-import   # skip gate 3, no n8n needed
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

from dotenv import load_dotenv

from eval.harness import run_gates

# find_dotenv() walks up from this file's own directory, so this finds
# flowforge/.env regardless of the process's working directory or shell.
load_dotenv()

EVAL_DIR = Path(__file__).resolve().parent
HELDOUT = EVAL_DIR.parent / "data" / "out" / "heldout.jsonl"


def load_heldout_targets(path: Path) -> list[str]:
    """Return the assistant (ground-truth) JSON string for every heldout row."""
    targets = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            messages = json.loads(line)["messages"]
            targets.append(next(m["content"] for m in messages if m["role"] == "assistant"))
    return targets


def main() -> None:
    p = argparse.ArgumentParser(description="Quality-check heldout ground truth against the gate cascade.")
    p.add_argument("--n", type=int, default=30)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--no-import", action="store_true", help="skip gate 3 (no n8n available)")
    args = p.parse_args()

    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    all_targets = load_heldout_targets(HELDOUT)
    sample = random.Random(args.seed).sample(all_targets, min(args.n, len(all_targets)))
    print(f"Loaded {len(all_targets)} heldout examples, checking {len(sample)} (seed={args.seed}).")

    counts = {"gate1": 0, "gate2": 0, "gate3": 0}
    gate3_failures: list[dict] = []

    for i, target in enumerate(sample, 1):
        result = run_gates(target, live_import=not args.no_import)
        counts["gate1"] += result.json_valid
        counts["gate2"] += result.schema_valid
        counts["gate3"] += result.import_valid
        status = f"json={result.json_valid} schema={result.schema_valid} import={result.import_valid}"
        print(f"  [{i}/{len(sample)}] {status}")
        if not args.no_import and result.schema_valid and not result.import_valid:
            gate3_failures.append({"index": i, "errors": result.errors, "target": target[:2000]})

    n = len(sample)
    print("\n=== quality_check results ===")
    for gate in ("gate1", "gate2", "gate3"):
        if gate == "gate3" and args.no_import:
            print("gate3: skipped (--no-import)")
            continue
        pct = counts[gate] / n if n else 0.0
        print(f"{gate}: {counts[gate]}/{n} ({pct:.1%})")

    if gate3_failures:
        print(f"\n=== {len(gate3_failures)} gate-3 failures (schema-valid but import rejected) ===")
        for f in gate3_failures:
            print(f"\n--- example #{f['index']} ---")
            print("errors:", f["errors"])
            print("target (truncated):", f["target"])


if __name__ == "__main__":
    main()
