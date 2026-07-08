"""Extract a workflow JSON object from raw model output.

Models sometimes wrap JSON in markdown fences or add stray prose despite the
system prompt. Shared by the eval harness and the backend /generate route so
both judge model output identically.
"""
from __future__ import annotations

import json


def extract_json(text: str) -> dict | None:
    """Return the first parseable JSON object in `text`, or None.

    Tries, in order: the whole string, fenced ```json blocks, and the outermost
    {...} span. Only dict results count - a bare list/string is not a workflow.
    """
    candidates = [text.strip()]

    if "```" in text:
        for chunk in text.split("```")[1::2]:  # every fenced block
            chunk = chunk.strip()
            if chunk.startswith("json"):
                chunk = chunk[4:].strip()
            candidates.append(chunk)

    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        candidates.append(text[start : end + 1])

    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except (json.JSONDecodeError, ValueError):
            continue
        if isinstance(parsed, dict):
            return parsed
    return None
