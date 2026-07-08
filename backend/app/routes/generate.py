"""POST /generate - natural language in, validated n8n workflow JSON out."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.generation import generate_validated

router = APIRouter()


class GenerateRequest(BaseModel):
    description: str = Field(..., min_length=3, description="Plain-language automation description.")


class Gates(BaseModel):
    json_valid: bool
    schema_valid: bool


class GenerateResponse(BaseModel):
    workflow: dict[str, Any] | None
    raw: str
    gates: Gates
    errors: list[str]
    attempts: int


@router.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest) -> GenerateResponse:
    try:
        result = generate_validated(req.description)
    except Exception as e:  # model endpoint unreachable, auth failure, etc.
        raise HTTPException(status_code=502, detail=f"model endpoint error: {e}") from e

    return GenerateResponse(
        workflow=result.workflow,
        raw=result.raw,
        gates=Gates(json_valid=result.json_valid, schema_valid=result.schema_valid),
        errors=result.errors[:8],
        attempts=result.attempts,
    )
