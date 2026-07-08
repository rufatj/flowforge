"""Generate-and-validate service behind POST /generate.

Calls the model once, judges the output with eval gates 1-2, and if either
fails retries exactly once with a stricter reminder appended to the request.
Returns whichever attempt scored better, so a failed retry can't make the
response worse than the first try.
"""
from __future__ import annotations

from dataclasses import dataclass

from eval.gates import gate_json_valid, gate_schema_valid

from app.model_client import generate_workflow

STRICT_REMINDER = (
    "IMPORTANT: your previous answer was not a valid n8n workflow. Return ONLY "
    "one JSON object, no markdown fences, no prose. It must have a non-empty "
    "'nodes' array (each node: name, type, typeVersion, position, parameters) "
    "and a 'connections' object keyed by source node NAME with double-nested "
    "target arrays."
)


@dataclass
class GenerationResult:
    workflow: dict | None
    raw: str
    json_valid: bool
    schema_valid: bool
    errors: list[str]
    attempts: int

    @staticmethod
    def judge(raw: str, attempts: int) -> "GenerationResult":
        json_ok, workflow = gate_json_valid(raw)
        schema_ok, errors = gate_schema_valid(workflow) if json_ok else (False, ["no parseable JSON object"])
        return GenerationResult(workflow, raw, json_ok, schema_ok, errors, attempts)

    @property
    def score(self) -> int:
        return int(self.json_valid) + int(self.schema_valid)


def generate_validated(description: str) -> GenerationResult:
    """One model call, plus one stricter retry if gates 1-2 don't both pass."""
    first = GenerationResult.judge(generate_workflow(description), attempts=1)
    if first.schema_valid:
        return first

    retry_raw = generate_workflow(description, extra_reminder=STRICT_REMINDER)
    retry = GenerationResult.judge(retry_raw, attempts=2)
    return retry if retry.score >= first.score else GenerationResult(
        first.workflow, first.raw, first.json_valid, first.schema_valid, first.errors, 2
    )
