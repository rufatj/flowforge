"""POST /testform (webhook test form HTML) and GET /results (eval numbers)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.formgen import build_test_form

router = APIRouter()

# Repo root was located by app/__init__ (it found eval/ there); results.json
# lives inside eval/results both locally and in the Docker image.
_RESULTS_PATH = next(
    (p / "eval" / "results" / "results.json" for p in Path(__file__).resolve().parents
     if (p / "eval").is_dir()),
    None,
)


class TestFormRequest(BaseModel):
    workflow: dict[str, Any]


@router.post("/testform", response_class=HTMLResponse)
def testform(req: TestFormRequest) -> HTMLResponse:
    return HTMLResponse(content=build_test_form(req.workflow))


@router.get("/results")
def results() -> dict[str, Any]:
    if _RESULTS_PATH and _RESULTS_PATH.exists():
        return json.loads(_RESULTS_PATH.read_text(encoding="utf-8"))
    return {"runs": []}
