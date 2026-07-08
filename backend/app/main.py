"""FastAPI entry point for FlowForge.

Routes are kept thin and live in app/routes/*. All real logic belongs in the
modules (model_client, n8n, formgen). This file only wires them together.
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.routes import generate, health, import_workflow, testform

app = FastAPI(
    title="FlowForge API",
    description="Turn natural language into importable n8n workflow JSON.",
    version=__version__,
)

# The frontend is served from a different origin (Vite dev server), so allow it.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Each concern gets its own router module.
app.include_router(health.router, tags=["health"])
app.include_router(generate.router, tags=["generate"])
app.include_router(import_workflow.router, tags=["import"])
app.include_router(testform.router, tags=["testform"])


@app.get("/")
def root() -> dict[str, str]:
    """Tiny landing payload so the base URL is not a 404."""
    return {"name": "FlowForge API", "version": __version__, "docs": "/docs"}
