"""Known-good n8n node types, derived from the cleaned dataset.

The allowlist is data-driven (same rule as data/clean.py): every node type that
survived cleaning is trusted. Cached to eval/known_node_types.json so the gates
work without the 22MB clean.jsonl present (e.g. inside the backend container).
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent
CLEAN_JSONL = EVAL_DIR.parent / "data" / "out" / "clean.jsonl"
CACHE_FILE = EVAL_DIR / "known_node_types.json"


def _build_from_clean() -> set[str]:
    types: set[str] = set()
    with CLEAN_JSONL.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            types.update(json.loads(line).get("node_types", []))
    return types


@lru_cache(maxsize=1)
def known_node_types() -> frozenset[str]:
    """Load the allowlist, rebuilding the cache from clean.jsonl when possible."""
    if CLEAN_JSONL.exists():
        types = _build_from_clean()
        CACHE_FILE.write_text(json.dumps(sorted(types), indent=0), encoding="utf-8")
        return frozenset(types)
    if CACHE_FILE.exists():
        return frozenset(json.loads(CACHE_FILE.read_text(encoding="utf-8")))
    raise FileNotFoundError(
        f"Neither {CLEAN_JSONL} nor {CACHE_FILE} exists - run data/clean.py first."
    )


if __name__ == "__main__":
    types = known_node_types()
    print(f"{len(types)} known node types (cache: {CACHE_FILE.name})")
