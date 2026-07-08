"""collect.py — build a text-to-n8n-workflow dataset from n8n's public
community template library (api.n8n.io).

Two endpoints are involved, and they are NOT the same shape (verified by
inspecting live responses on 2026-07-07):

  GET https://api.n8n.io/templates/search?page=N&rows=R
      -> {"totalWorkflows": int, "workflows": [{"id", "name", "description",
          "user", "createdAt", "nodes" (a codex-decorated SUMMARY list, not the
          real node objects), ...}]}
      This is a lightweight listing. `rows` is capped at 250 by the server
      (confirmed: rows=500 returns a 422 "Only upto 250 hits can be fetched
      per page"). Paginate until `workflows` comes back empty.

  GET https://api.n8n.io/workflows/templates/{id}
      -> {"id", "name", "workflow": {"meta", "nodes", "pinData", "connections"}}
      This FLAT detail endpoint returns the real importable node objects
      (id/name/type/position/parameters/typeVersion) and the real
      `connections`. Prefer this one over /templates/workflows/{id}, which
      double-nests the same data one level deeper (workflow.workflow).

This is NOT the self-hosted n8n management API (/api/v1/...); no API key is
needed here.

Usage:
    python data/collect.py --limit 5        # smoke test, 5 new templates
    python data/collect.py                  # full collection (resumable)
    python data/collect.py --rows 250 --delay 0.5

Output: data/out/raw_templates.jsonl (appended to; resumable), one JSON
object per line:
    {"source": "api", "id": "<template id>", "name", "description",
     "workflow": {"nodes": [...], "connections": {...}},
     "node_types": [...unique, sorted...], "node_count": int}

Resume: ids already present in raw_templates.jsonl are loaded at start and
skipped, so re-running only fetches templates not yet collected. --limit
caps the number of NEW templates fetched in this run.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Iterator

import requests

BASE_URL = "https://api.n8n.io"
SEARCH_PATH = "/templates/search"
DETAIL_PATH = "/workflows/templates/{id}"

USER_AGENT = (
    "FlowForge-DatasetCollector/0.1 "
    "(+AMD hackathon dataset collection; contact: rufatjabra@gmail.com)"
)

OUT_DIR = Path(__file__).resolve().parent / "out"
RAW_OUT = OUT_DIR / "raw_templates.jsonl"

MAX_ROWS_PER_PAGE = 250
MAX_RETRIES = 3


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json"})
    return s


def _get_json(session: requests.Session, url: str, params: dict | None = None) -> dict | None:
    """GET with a small retry/backoff loop. Returns None if all attempts fail."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = session.get(url, params=params, timeout=30)
            if resp.status_code == 429:
                wait = 2**attempt
                print(f"  rate limited, backing off {wait}s...", file=sys.stderr)
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            print(f"  request failed (attempt {attempt}/{MAX_RETRIES}): {e}", file=sys.stderr)
            time.sleep(1.5 * attempt)
    return None


def iter_template_listings(session: requests.Session, rows: int, delay: float) -> Iterator[dict]:
    """Yield lightweight listing entries (id/name/description) across all pages."""
    page = 1
    rows = min(rows, MAX_ROWS_PER_PAGE)
    while True:
        data = _get_json(session, f"{BASE_URL}{SEARCH_PATH}", {"page": page, "rows": rows})
        if not data:
            break
        workflows = data.get("workflows") or []
        if not workflows:
            break
        for w in workflows:
            yield w
        page += 1
        time.sleep(delay)


def fetch_workflow_detail(session: requests.Session, template_id: int) -> dict | None:
    url = f"{BASE_URL}{DETAIL_PATH.format(id=template_id)}"
    return _get_json(session, url)


def load_existing_ids() -> set[str]:
    """Read ids already in raw_templates.jsonl so re-runs don't refetch them."""
    if not RAW_OUT.exists():
        return set()
    ids: set[str] = set()
    with RAW_OUT.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                ids.add(json.loads(line)["id"])
            except (json.JSONDecodeError, KeyError):
                continue
    return ids


def collect(limit: int | None, rows: int, delay: float) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    seen_ids = load_existing_ids()
    print(f"Resuming: {len(seen_ids)} templates already collected.")

    session = _session()
    new_count = 0

    with RAW_OUT.open("a", encoding="utf-8") as out_f:
        for listing in iter_template_listings(session, rows=rows, delay=delay):
            if limit is not None and new_count >= limit:
                break

            template_id = str(listing.get("id"))
            if template_id in seen_ids:
                continue

            detail = fetch_workflow_detail(session, listing["id"])
            time.sleep(delay)
            if not detail or "workflow" not in detail:
                print(f"  skip {template_id}: no detail returned", file=sys.stderr)
                continue

            inner = detail["workflow"]
            nodes = inner.get("nodes") or []
            connections = inner.get("connections") or {}
            if not nodes:
                print(f"  skip {template_id}: zero nodes", file=sys.stderr)
                continue

            node_types = sorted({n["type"] for n in nodes if "type" in n})
            record = {
                "source": "api",
                "id": template_id,
                "name": listing.get("name") or detail.get("name") or "",
                "description": listing.get("description") or "",
                "workflow": {"nodes": nodes, "connections": connections},
                "node_types": node_types,
                "node_count": len(nodes),
            }
            out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
            out_f.flush()
            seen_ids.add(template_id)
            new_count += 1

            if new_count % 25 == 0:
                print(f"  collected {new_count} new templates so far...")

    print(f"Done. {new_count} new templates collected this run.")
    log_stats()


def log_stats() -> None:
    """Print total count, node-count distribution, and top 30 node types
    across the ENTIRE accumulated raw_templates.jsonl (not just this run)."""
    if not RAW_OUT.exists():
        print("No data collected yet.")
        return

    node_counts: list[int] = []
    type_counter: Counter[str] = Counter()
    total = 0

    with RAW_OUT.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            total += 1
            nodes = record.get("workflow", {}).get("nodes", [])
            node_counts.append(len(nodes))
            for n in nodes:
                t = n.get("type")
                if t:
                    type_counter[t] += 1

    print("\n=== Dataset stats (data/out/raw_templates.jsonl) ===")
    print(f"Total templates collected: {total}")

    if node_counts:
        node_counts.sort()
        n = len(node_counts)
        mean = sum(node_counts) / n
        median = node_counts[n // 2]
        print(
            f"Node count: min={node_counts[0]} max={node_counts[-1]} "
            f"mean={mean:.1f} median={median}"
        )

        buckets = [(0, 2), (3, 5), (6, 10), (11, 15), (16, 20), (21, 10**9)]
        for lo, hi in buckets:
            count = sum(1 for c in node_counts if lo <= c <= hi)
            label = f"{lo}-{hi}" if hi < 10**9 else f"{lo}+"
            print(f"  {label:>8} nodes: {count}")

    print("\nTop 30 node types:")
    for node_type, count in type_counter.most_common(30):
        print(f"  {count:>5}  {node_type}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect n8n workflow templates from api.n8n.io.")
    parser.add_argument("--limit", type=int, default=None, help="Max NEW templates to fetch this run.")
    parser.add_argument("--rows", type=int, default=100, help="Rows per search page (server max 250).")
    parser.add_argument("--delay", type=float, default=0.4, help="Seconds to sleep between requests.")
    args = parser.parse_args()
    collect(limit=args.limit, rows=args.rows, delay=args.delay)


if __name__ == "__main__":
    main()
