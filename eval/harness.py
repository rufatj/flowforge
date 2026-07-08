"""Three-gate evaluation harness - the project's proof engine.

Given raw model output, runs:
  Gate 1  json_valid    - a JSON object can be extracted (eval/gates.py)
  Gate 2  schema_valid  - n8n structure, known types, correct wiring
  Gate 3  import_valid  - a live n8n instance accepts it via REST API

Gates 1-2 are pure/local. Gate 3 needs N8N_API_URL + N8N_API_KEY and a
running n8n; pass live_import=False to skip it (used by backend /generate
and by GRPO reward when offline).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import requests

from eval.gates import gate_json_valid, gate_schema_valid
from eval.n8n_client import N8nClient


@dataclass
class GateResult:
    json_valid: bool = False
    schema_valid: bool = False
    import_valid: bool = False
    errors: list[str] = field(default_factory=list)
    workflow: dict | None = None

    def as_dict(self) -> dict:
        return {
            "json_valid": self.json_valid,
            "schema_valid": self.schema_valid,
            "import_valid": self.import_valid,
            "errors": self.errors[:8],
        }


def gate_import_valid(workflow: dict, client: N8nClient | None = None) -> tuple[bool, list[str]]:
    """Gate 3: POST to n8n, verify node count survived, then always delete."""
    client = client or N8nClient()
    try:
        created = client.create_workflow(workflow)
    except requests.HTTPError as e:
        detail = e.response.text[:200] if e.response is not None else str(e)
        return False, [f"n8n rejected import: {detail}"]
    except requests.RequestException as e:
        return False, [f"n8n unreachable: {e}"]

    workflow_id = created.get("id")
    errors: list[str] = []
    sent, got = len(workflow.get("nodes", [])), len(created.get("nodes", []))
    if got != sent:
        errors.append(f"import silently dropped nodes (sent {sent}, stored {got})")
    if workflow_id:
        client.delete_workflow(str(workflow_id))
    else:
        errors.append("n8n response had no workflow id")
    return not errors, errors


def run_gates(model_output: str, *, live_import: bool = True, client: N8nClient | None = None) -> GateResult:
    """Run the gate cascade; later gates only run if earlier ones pass."""
    result = GateResult()

    result.json_valid, workflow = gate_json_valid(model_output)
    if not result.json_valid:
        result.errors.append("no parseable JSON object in output")
        return result
    result.workflow = workflow

    result.schema_valid, schema_errors = gate_schema_valid(workflow)
    result.errors.extend(schema_errors)
    if not result.schema_valid or not live_import:
        return result

    result.import_valid, import_errors = gate_import_valid(workflow, client)
    result.errors.extend(import_errors)
    return result
