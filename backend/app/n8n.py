"""Backend-side n8n glue: import via the shared eval client + URL helpers.

The actual REST logic lives in eval/n8n_client.py (single source of truth,
also used by gate 3). This module only adds what the API responses need:
editor links and webhook trigger URLs extracted from workflow nodes.
"""
from __future__ import annotations

from typing import Any

from eval.n8n_client import N8nClient

from app import config

WEBHOOK_NODE_TYPES = ("n8n-nodes-base.webhook", "n8n-nodes-base.formTrigger")


def import_workflow(workflow: dict[str, Any]) -> dict[str, Any]:
    """Create the workflow in n8n; returns {'id': ..., 'nodes': [...], ...}.

    Raises requests.HTTPError / requests.RequestException upward - the route
    turns those into clean HTTP error responses.
    """
    client = N8nClient(base_url=config.N8N_API_URL, api_key=config.N8N_API_KEY)
    return client.create_workflow(workflow)


def editor_url(workflow_id: str) -> str:
    return f"{config.N8N_EDITOR_URL.rstrip('/')}/workflow/{workflow_id}"


def webhook_nodes(workflow: dict[str, Any]) -> list[dict[str, Any]]:
    nodes = workflow.get("nodes")
    if not isinstance(nodes, list):
        return []
    return [n for n in nodes if isinstance(n, dict) and n.get("type") in WEBHOOK_NODE_TYPES]


def webhook_urls(workflow: dict[str, Any]) -> list[str]:
    """Production trigger URLs for every webhook-style node with a path."""
    base = config.N8N_EDITOR_URL.rstrip("/")
    urls = []
    for node in webhook_nodes(workflow):
        path = node.get("parameters", {}).get("path") or node.get("webhookId")
        if path:
            prefix = "form" if node.get("type") == "n8n-nodes-base.formTrigger" else "webhook"
            urls.append(f"{base}/{prefix}/{path}")
    return urls
