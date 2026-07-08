"""POST /import - push a generated workflow into the live n8n instance."""
from __future__ import annotations

from typing import Any

import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app import n8n

router = APIRouter()


class ImportRequest(BaseModel):
    workflow: dict[str, Any]


class ImportResponse(BaseModel):
    n8n_workflow_id: str
    editor_url: str
    webhook_urls: list[str]
    node_count: int


@router.post("/import", response_model=ImportResponse)
def import_workflow(req: ImportRequest) -> ImportResponse:
    try:
        created = n8n.import_workflow(req.workflow)
    except requests.HTTPError as e:
        detail = e.response.text[:300] if e.response is not None else str(e)
        raise HTTPException(status_code=422, detail=f"n8n rejected the workflow: {detail}") from e
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"n8n unreachable: {e}") from e

    workflow_id = str(created.get("id", ""))
    if not workflow_id:
        raise HTTPException(status_code=502, detail="n8n accepted the import but returned no id")

    return ImportResponse(
        n8n_workflow_id=workflow_id,
        editor_url=n8n.editor_url(workflow_id),
        webhook_urls=n8n.webhook_urls(req.workflow),
        node_count=len(created.get("nodes", [])),
    )
