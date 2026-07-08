"""GET /health — works immediately, no model or n8n key required."""
from __future__ import annotations

from fastapi import APIRouter

from app import __version__
from app.model_client import active_mode

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    """Liveness probe used by docker-compose and the frontend."""
    return {
        "status": "ok",
        "version": __version__,
        "model_mode": active_mode(),
    }
