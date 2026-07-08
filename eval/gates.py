"""Gates 1 and 2: JSON validity and n8n schema validity.

Gate 2 mirrors what n8n actually requires plus the documented LLM failure
modes: hallucinated node types, connections keyed by id instead of name,
missing double-nesting, and AI sub-nodes wired via "main" instead of ai_*.
Calibrated so that real workflows from data/out/clean.jsonl pass.
"""
from __future__ import annotations

from eval.allowlist import known_node_types
from eval.json_extract import extract_json

VALID_CONNECTION_TYPES = {
    "main", "error", "ai_languageModel", "ai_tool", "ai_memory",
    "ai_outputParser", "ai_embedding", "ai_retriever", "ai_textSplitter",
    "ai_document", "ai_vectorStore", "ai_chain", "ai_reranker",
}

# Node-type patterns that are AI sub-nodes: they must attach via ai_*, not main.
# NOTE: langchain.memoryManager is a regular main-flow node (calibrated on
# clean.jsonl), so ".memory" alone would over-match - it is excluded below.
_AI_SUBNODE_MARKERS = ("lmChat", ".memory", ".embeddings", ".outputParser")
_MAIN_FLOW_EXCEPTIONS = ("memoryManager",)


def gate_json_valid(text: str) -> tuple[bool, dict | None]:
    """Gate 1: the output contains a parseable JSON object."""
    workflow = extract_json(text)
    return workflow is not None, workflow


def _requires_ai_connection(node_type: str) -> bool:
    if node_type.endswith(_MAIN_FLOW_EXCEPTIONS):
        return False
    if node_type.endswith("Tool") or node_type.startswith("@n8n/n8n-nodes-langchain.tool"):
        return True
    return node_type.startswith("@n8n/n8n-nodes-langchain.") and any(
        m in node_type for m in _AI_SUBNODE_MARKERS
    )


def _check_node(node: object, errors: list[str]) -> str | None:
    """Validate one node; return its name if usable."""
    if not isinstance(node, dict):
        errors.append("node is not an object")
        return None
    for key in ("name", "type", "position", "parameters"):
        if key not in node:
            errors.append(f"node missing '{key}'")
    pos = node.get("position")
    if not (isinstance(pos, list) and len(pos) == 2):
        errors.append(f"node '{node.get('name')}' position is not a [x, y] pair")
    return node.get("name")


def _check_connections(connections: dict, names: set[str], types_by_name: dict, errors: list[str]) -> None:
    for source, by_type in connections.items():
        if source not in names:
            errors.append(f"connection source '{source}' is not a node name")
            continue
        if not isinstance(by_type, dict):
            errors.append(f"connections['{source}'] is not an object")
            continue
        for conn_type, outputs in by_type.items():
            if conn_type not in VALID_CONNECTION_TYPES:
                errors.append(f"unknown connection type '{conn_type}'")
            if _requires_ai_connection(types_by_name.get(source, "")) and conn_type == "main":
                errors.append(f"AI sub-node '{source}' wired via 'main' instead of ai_*")
            if not isinstance(outputs, list) or any(not isinstance(t, list) for t in outputs):
                errors.append(f"connections['{source}']['{conn_type}'] is not double-nested")
                continue
            for targets in outputs:
                for t in targets:
                    if not isinstance(t, dict) or t.get("node") not in names:
                        errors.append(f"connection target from '{source}' references unknown node")


def gate_schema_valid(workflow: dict) -> tuple[bool, list[str]]:
    """Gate 2: structure, known node types, and connection wiring all check out."""
    errors: list[str] = []
    nodes = workflow.get("nodes")
    connections = workflow.get("connections")
    if not isinstance(nodes, list) or not nodes:
        return False, ["'nodes' missing, not a list, or empty"]
    if not isinstance(connections, dict):
        return False, ["'connections' missing or not an object"]

    allowlist = known_node_types()
    names: set[str] = set()
    types_by_name: dict[str, str] = {}
    for node in nodes:
        name = _check_node(node, errors)
        if name:
            names.add(name)
            types_by_name[name] = node.get("type", "")
        node_type = node.get("type") if isinstance(node, dict) else None
        if node_type and node_type not in allowlist:
            errors.append(f"unknown node type '{node_type}'")

    _check_connections(connections, names, types_by_name, errors)
    return not errors, errors
