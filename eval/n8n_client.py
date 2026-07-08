"""Thin client for the self-hosted n8n REST API (gate 3 + backend /import).

Import quirks handled here (from n8n GitHub issues #14002/#19587):
  - Send ONLY name, nodes, connections, settings. Anything else (id, active,
    tags, staticData, meta, pinData) triggers 400 "must NOT have additional
    properties".
  - settings must exist; {"executionOrder": "v1"} is the safe default.
  - A 2xx can still hide a silently-empty import, so callers should compare
    the returned node count (create_workflow returns the full response body).
"""
from __future__ import annotations

import os
from typing import Any

import requests

IMPORTABLE_KEYS = ("name", "nodes", "connections", "settings")


def sanitize_workflow(workflow: dict[str, Any], fallback_name: str = "FlowForge workflow") -> dict[str, Any]:
    """Reduce a workflow to exactly the fields n8n's create endpoint accepts."""
    cleaned = {k: workflow[k] for k in IMPORTABLE_KEYS if k in workflow}
    cleaned.setdefault("name", fallback_name)
    cleaned.setdefault("connections", {})
    settings = cleaned.get("settings")
    if not isinstance(settings, dict):
        settings = {}
    settings.setdefault("executionOrder", "v1")
    cleaned["settings"] = settings
    return cleaned


class N8nClient:
    def __init__(self, base_url: str | None = None, api_key: str | None = None, timeout: int = 30) -> None:
        self.base_url = (base_url or os.environ.get("N8N_API_URL", "http://localhost:5678/api/v1")).rstrip("/")
        self.api_key = api_key or os.environ.get("N8N_API_KEY", "")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"X-N8N-API-KEY": self.api_key, "Content-Type": "application/json"})

    def create_workflow(self, workflow: dict[str, Any]) -> dict[str, Any]:
        """POST a sanitized workflow. Returns n8n's response body (has 'id').

        Raises requests.HTTPError on rejection - callers treat that as gate 3
        failure and read the error detail from the exception's response.
        """
        resp = self.session.post(
            f"{self.base_url}/workflows", json=sanitize_workflow(workflow), timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()

    def delete_workflow(self, workflow_id: str) -> None:
        """Best-effort cleanup; never raises (eval must not leak workflows)."""
        try:
            self.session.delete(f"{self.base_url}/workflows/{workflow_id}", timeout=self.timeout)
        except requests.RequestException:
            pass
