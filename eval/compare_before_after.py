"""compare_before_after.py — one-command base vs fine-tuned eval comparison.

Runs BOTH endpoints over the same heldout prompts through the three-gate
harness, saves a side-by-side eval/results/comparison.json, and prints a
summary table. Both endpoints must be OpenAI-compatible (vLLM, Fireworks,
or serving/serve_fallback.py).

Usage (once both servers are up on the GPU pod):
    python -m eval.compare_before_after \
        --base-url  http://localhost:8000/v1 --base-model  gemma-base \
        --ft-url    http://localhost:8001/v1 --ft-model    flowforge \
        --limit 50
Add --no-import to skip gate 3 when no n8n is reachable from the pod.
Gate 3 needs N8N_API_URL + N8N_API_KEY (loaded from .env automatically).
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

# run_eval already calls load_dotenv() at import time.
from eval.run_eval import evaluate, load_heldout_prompts
from eval.model_endpoint import ModelEndpoint

COMPARISON_OUT = Path(__file__).resolve().parent / "results" / "comparison.json"
GATES = ("gate1", "gate2", "gate3")
GATE_LABELS = {"gate1": "JSON valid", "gate2": "schema valid", "gate3": "n8n import"}


def run_side(label: str, base_url: str, model: str, api_key: str,
             prompts: list[str], live_import: bool) -> dict:
    print(f"\n--- {label}: {model} @ {base_url} ({len(prompts)} prompts) ---")
    endpoint = ModelEndpoint(base_url, model, api_key)
    counts, examples = evaluate(endpoint, prompts, live_import)
    total = len(prompts)
    return {
        "label": label, "model": model, "base_url": base_url, "total": total,
        **{g: round(counts[g] / total, 4) if total else 0.0 for g in GATES},
        "examples": examples,
    }


def print_table(base: dict, ft: dict) -> None:
    print(f"\n{'Gate':<22}{'base':>10}{'fine-tuned':>14}{'delta':>10}")
    print("-" * 56)
    for g in GATES:
        delta = ft[g] - base[g]
        print(f"{g} ({GATE_LABELS[g]})".ljust(22)
              + f"{base[g]:>9.1%}{ft[g]:>13.1%}{delta:>+10.1%}")
    print("-" * 56)
    print(f"n = {base['total']} heldout prompts per side")


def main() -> None:
    p = argparse.ArgumentParser(description="Side-by-side base vs fine-tuned three-gate eval.")
    p.add_argument("--base-url", required=True, help="OpenAI-compatible URL of the BASE model")
    p.add_argument("--base-model", required=True)
    p.add_argument("--base-api-key", default="EMPTY")
    p.add_argument("--ft-url", required=True, help="OpenAI-compatible URL of the FINE-TUNED model")
    p.add_argument("--ft-model", required=True)
    p.add_argument("--ft-api-key", default="EMPTY")
    p.add_argument("--limit", type=int, default=None, help="Max heldout prompts (default: all 810)")
    p.add_argument("--no-import", action="store_true", help="skip gate 3 (no n8n available)")
    args = p.parse_args()

    prompts = load_heldout_prompts(args.limit)
    live_import = not args.no_import

    base = run_side("base", args.base_url, args.base_model, args.base_api_key, prompts, live_import)
    ft = run_side("fine-tuned", args.ft_url, args.ft_model, args.ft_api_key, prompts, live_import)

    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "gate3_live_import": live_import,
        "base": base,
        "fine_tuned": ft,
        "delta": {g: round(ft[g] - base[g], 4) for g in GATES},
    }
    COMPARISON_OUT.parent.mkdir(parents=True, exist_ok=True)
    COMPARISON_OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    print_table(base, ft)
    print(f"Saved to {COMPARISON_OUT}")


if __name__ == "__main__":
    main()
