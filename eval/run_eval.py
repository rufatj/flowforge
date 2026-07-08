"""Run the three-gate eval over the heldout set against a model endpoint.

Usage (baseline via Fireworks, then fine-tuned via AMD vLLM):
    python -m eval.run_eval --label base-gemma --base-url https://api.fireworks.ai/inference/v1 \
        --model <fireworks-model-id> --api-key $FIREWORKS_API_KEY --limit 10
    python -m eval.run_eval --label flowforge-sft --base-url http://<mi300x>:8000/v1 --model flowforge

Appends a run into eval/results/results.json:
    {"runs": [{"label", "model", "gate1", "gate2", "gate3", "total", "examples": [...]}]}
Re-running with an existing label replaces that run. Pass --no-import to skip
gate 3 when no n8n instance is reachable.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

from eval.harness import run_gates
from eval.model_endpoint import ModelEndpoint

# find_dotenv() walks up from this file's own directory, so this finds
# flowforge/.env regardless of the process's working directory or shell.
load_dotenv()

EVAL_DIR = Path(__file__).resolve().parent
HELDOUT = EVAL_DIR.parent / "data" / "out" / "heldout.jsonl"
RESULTS = EVAL_DIR / "results" / "results.json"
N_EXAMPLES_SAVED = 5


def load_heldout_prompts(limit: int | None) -> list[str]:
    prompts = []
    with HELDOUT.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                messages = json.loads(line)["messages"]
                prompts.append(next(m["content"] for m in messages if m["role"] == "user"))
    return prompts[:limit] if limit else prompts


def evaluate(endpoint: ModelEndpoint, prompts: list[str], live_import: bool) -> tuple[dict, list[dict]]:
    counts = {"gate1": 0, "gate2": 0, "gate3": 0}
    examples: list[dict] = []
    for i, prompt in enumerate(prompts, 1):
        try:
            output = endpoint.generate(prompt)
        except RuntimeError as e:
            print(f"  [{i}/{len(prompts)}] generation error: {e}", file=sys.stderr)
            output = ""
        result = run_gates(output, live_import=live_import)
        counts["gate1"] += result.json_valid
        counts["gate2"] += result.schema_valid
        counts["gate3"] += result.import_valid
        if len(examples) < N_EXAMPLES_SAVED:
            examples.append({"prompt": prompt, "output": output[:2000], "gates": result.as_dict()})
        print(f"  [{i}/{len(prompts)}] json={result.json_valid} schema={result.schema_valid} import={result.import_valid}")
    return counts, examples


def save_run(label: str, model: str, counts: dict, total: int, examples: list[dict]) -> dict:
    run = {"label": label, "model": model, "total": total,
           **{g: round(counts[g] / total, 4) if total else 0.0 for g in ("gate1", "gate2", "gate3")},
           "examples": examples}
    data = {"runs": []}
    if RESULTS.exists():
        data = json.loads(RESULTS.read_text(encoding="utf-8"))
        data.setdefault("runs", [])
    data["runs"] = [r for r in data["runs"] if r.get("label") != label] + [run]
    data.pop("_note", None)
    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    RESULTS.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return run


def main() -> None:
    p = argparse.ArgumentParser(description="FlowForge three-gate eval")
    p.add_argument("--label", required=True)
    p.add_argument("--base-url", required=True)
    p.add_argument("--model", required=True)
    p.add_argument("--api-key", default="EMPTY")
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--no-import", action="store_true", help="skip gate 3 (no n8n available)")
    args = p.parse_args()

    prompts = load_heldout_prompts(args.limit)
    print(f"Evaluating {len(prompts)} heldout prompts against {args.model} @ {args.base_url}")
    endpoint = ModelEndpoint(args.base_url, args.model, args.api_key)
    counts, examples = evaluate(endpoint, prompts, live_import=not args.no_import)
    run = save_run(args.label, args.model, counts, len(prompts), examples)
    print(f"\n{args.label}: gate1={run['gate1']:.1%} gate2={run['gate2']:.1%} gate3={run['gate3']:.1%} (n={run['total']})")
    print(f"Saved to {RESULTS}")


if __name__ == "__main__":
    main()
