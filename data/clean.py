"""clean.py — filter and normalize data/out/raw_templates.jsonl.

Two-pass design:
  Pass 1: parse every line, validate the `workflow` field is a well-formed
          {"nodes": [...], "connections": {...}} object, and REMOVE all
          n8n-nodes-base.stickyNote nodes (+ any connections that reference
          them) before anything else is measured. Sticky notes are free-text
          comments, not automation logic — the raw corpus carries thousands of
          them and they would confuse the model into generating decorative
          "note" nodes. While at it, build a known-good node-type allowlist:
          any type appearing in at least MIN_TEMPLATES_FOR_ALLOWLIST distinct
          templates (post-sticky-removal) is considered known. This adapts to
          whatever the real data contains instead of a hardcoded node list.
  Pass 2: apply the node-count range, the allowlist, and the description
          length filter; normalize credentials and any stray workflow-level
          envelope fields; write survivors to data/out/clean.jsonl.

Usage:
    python data/clean.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

RAW_IN = Path(__file__).resolve().parent / "out" / "raw_templates.jsonl"
CLEAN_OUT = Path(__file__).resolve().parent / "out" / "clean.jsonl"

STICKY_NOTE_TYPE = "n8n-nodes-base.stickyNote"

MIN_NODES = 2
MAX_NODES = 20
MIN_TEMPLATES_FOR_ALLOWLIST = 3
MIN_DESCRIPTION_LEN = 10

# Workflow-level fields that block n8n import if present on export; our own
# collectors never write these into the `workflow` sub-object (they only ever
# store nodes/connections there), but the HF source is inconsistent about what
# it embeds, so we strip defensively rather than assume our own schema holds.
ENVELOPE_FIELDS_TO_STRIP = ("id", "active", "tags", "versionId", "staticData", "meta", "pinData", "settings")


def _validate_workflow_shape(workflow: Any) -> tuple[list, dict] | None:
    """Return (nodes, connections) if `workflow` is well-formed, else None."""
    if not isinstance(workflow, dict):
        return None
    nodes = workflow.get("nodes")
    connections = workflow.get("connections")
    if not isinstance(nodes, list) or not isinstance(connections, dict):
        return None
    return nodes, connections


def remove_sticky_notes(nodes: list, connections: dict) -> tuple[list, dict, int]:
    """Strip stickyNote nodes and any connection entries that reference them.

    Connections are keyed by source node NAME, then connection type, then a
    double-nested array of {node, type, index} target dicts. We drop any
    top-level source key that names a removed node, and filter removed-node
    targets out of every remaining connection-type array, preserving the
    output-index structure (an emptied inner list is left as [] rather than
    collapsing the array, since that would shift output indices).
    """
    # A set of NAMES (for connection filtering, since connections reference
    # nodes by name) and a true instance COUNT (for accurate stats) are kept
    # separate: two sticky notes can share the same name (e.g. both left at
    # the default "Sticky Note"), which would otherwise undercount removals.
    removed_names = {n.get("name") for n in nodes if n.get("type") == STICKY_NOTE_TYPE}
    removed_count = sum(1 for n in nodes if n.get("type") == STICKY_NOTE_TYPE)
    kept_nodes = [n for n in nodes if n.get("type") != STICKY_NOTE_TYPE]

    cleaned_connections: dict = {}
    for source_name, by_type in connections.items():
        if source_name in removed_names or not isinstance(by_type, dict):
            continue
        new_by_type: dict = {}
        for conn_type, outputs in by_type.items():
            if not isinstance(outputs, list):
                continue
            new_outputs = []
            for targets in outputs:
                if not isinstance(targets, list):
                    new_outputs.append(targets)
                    continue
                new_targets = [t for t in targets if not (isinstance(t, dict) and t.get("node") in removed_names)]
                new_outputs.append(new_targets)
            # Drop the connection-type entry entirely if every output is empty.
            if any(o for o in new_outputs):
                new_by_type[conn_type] = new_outputs
        if new_by_type:
            cleaned_connections[source_name] = new_by_type

    return kept_nodes, cleaned_connections, removed_count


def strip_envelope_fields(workflow: dict) -> dict:
    """Defensively drop import-blocking envelope keys, if a source ever embeds them."""
    return {k: v for k, v in workflow.items() if k not in ENVELOPE_FIELDS_TO_STRIP}


def strip_credentials(node: dict) -> dict:
    """Replace credential entries with anonymized {id, name} placeholder stubs."""
    creds = node.get("credentials")
    if not isinstance(creds, dict):
        return node
    node = dict(node)
    node["credentials"] = {
        cred_type: {
            "id": "placeholder",
            "name": (cred_val.get("name", "credential") if isinstance(cred_val, dict) else "credential"),
        }
        for cred_type, cred_val in creds.items()
    }
    return node


def load_and_desticky(path: Path, drop_counts: Counter) -> list[dict]:
    """Pass 1: parse, validate shape, and remove sticky notes from every record."""
    interim: list[dict] = []
    total_sticky_removed = 0
    templates_with_sticky = 0

    if not path.exists():
        print(f"No input file at {path} — run data/collect.py or data/collect_hf.py first.", file=sys.stderr)
        return interim

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                drop_counts["invalid_json"] += 1
                continue

            shape = _validate_workflow_shape(record.get("workflow"))
            if shape is None:
                drop_counts["malformed_workflow_field"] += 1
                continue

            nodes, connections = shape
            nodes, connections, removed = remove_sticky_notes(nodes, connections)
            if removed:
                total_sticky_removed += removed
                templates_with_sticky += 1

            interim.append(
                {
                    "id": record.get("id"),
                    "source": record.get("source"),
                    "name": record.get("name") or "",
                    "description": record.get("description") or "",
                    "nodes": nodes,
                    "connections": connections,
                }
            )

    print(f"Removed {total_sticky_removed} stickyNote nodes across {templates_with_sticky} templates.")
    return interim


def build_allowlist(interim_records: list[dict]) -> set[str]:
    """A node type is known-good if it appears in >= MIN_TEMPLATES_FOR_ALLOWLIST distinct templates."""
    template_counts: Counter[str] = Counter()
    for rec in interim_records:
        types_in_template = {n.get("type") for n in rec["nodes"] if n.get("type")}
        for t in types_in_template:
            template_counts[t] += 1
    return {t for t, count in template_counts.items() if count >= MIN_TEMPLATES_FOR_ALLOWLIST}


def clean_records(interim_records: list[dict], allowlist: set[str], drop_counts: Counter) -> list[dict]:
    """Pass 2: node-count range, allowlist membership, description length, normalization."""
    kept: list[dict] = []
    for rec in interim_records:
        nodes = rec["nodes"]
        node_count = len(nodes)

        if node_count < MIN_NODES or node_count > MAX_NODES:
            drop_counts["node_count_out_of_range"] += 1
            continue

        if len(rec["description"].strip()) < MIN_DESCRIPTION_LEN:
            drop_counts["description_too_short"] += 1
            continue

        remaining_types = {n.get("type") for n in nodes if n.get("type")}
        if not remaining_types.issubset(allowlist):
            drop_counts["unknown_node_type"] += 1
            continue

        normalized_nodes = [strip_credentials(n) for n in nodes]
        workflow = strip_envelope_fields({"nodes": normalized_nodes, "connections": rec["connections"]})

        kept.append(
            {
                "id": rec["id"],
                "source": rec["source"],
                "name": rec["name"],
                "description": rec["description"],
                "workflow": workflow,
                "node_types": sorted(remaining_types),
                "node_count": node_count,
            }
        )
    return kept


def log_stats(kept: list[dict], drop_counts: Counter, total_raw_lines: int) -> None:
    total_kept = len(kept)
    total_dropped = sum(drop_counts.values())

    print("\n=== clean.py stats ===")
    print(f"Raw lines read:   {total_raw_lines}")
    print(f"Kept:             {total_kept}")
    print(f"Dropped:          {total_dropped}")
    print("Drop reasons:")
    for reason, count in drop_counts.most_common():
        print(f"  {count:>5}  {reason}")

    if not kept:
        return

    node_counts = sorted(r["node_count"] for r in kept)
    n = len(node_counts)
    mean = sum(node_counts) / n
    median = node_counts[n // 2]
    print(f"\nNode count after cleaning: min={node_counts[0]} max={node_counts[-1]} mean={mean:.1f} median={median}")

    buckets = [(2, 5), (6, 10), (11, 15), (16, 20)]
    for lo, hi in buckets:
        count = sum(1 for c in node_counts if lo <= c <= hi)
        print(f"  {lo}-{hi:>3} nodes: {count}")

    type_counter: Counter[str] = Counter()
    for r in kept:
        for n in r["workflow"]["nodes"]:
            t = n.get("type")
            if t:
                type_counter[t] += 1

    print("\nTop 30 node types after cleaning:")
    for node_type, count in type_counter.most_common(30):
        print(f"  {count:>5}  {node_type}")


def clean() -> None:
    drop_counts: Counter[str] = Counter()
    interim_records = load_and_desticky(RAW_IN, drop_counts)
    total_raw_lines = len(interim_records) + drop_counts["invalid_json"] + drop_counts["malformed_workflow_field"]

    allowlist = build_allowlist(interim_records)
    print(f"Built allowlist of {len(allowlist)} known-good node types "
          f"(>= {MIN_TEMPLATES_FOR_ALLOWLIST} templates each).")

    kept = clean_records(interim_records, allowlist, drop_counts)

    CLEAN_OUT.parent.mkdir(parents=True, exist_ok=True)
    with CLEAN_OUT.open("w", encoding="utf-8") as out_f:
        for record in kept:
            out_f.write(json.dumps(record, ensure_ascii=False) + "\n")

    log_stats(kept, drop_counts, total_raw_lines)


if __name__ == "__main__":
    clean()
