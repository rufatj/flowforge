"""Central configuration, read from environment variables.

Keeping this in one place means routes and clients never touch os.environ
directly. Values are read once at import time.
"""
from __future__ import annotations

import os

from dotenv import load_dotenv

# find_dotenv() walks up from this file's own directory, so this finds
# flowforge/.env regardless of the process's working directory or shell.
load_dotenv()


def _get(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


# Which model backend to route to: "fireworks" (dev) or "amd" (demo/judging).
MODEL_MODE: str = _get("MODEL_MODE", "fireworks").lower()

# Fireworks (OpenAI-compatible).
FIREWORKS_API_KEY: str = _get("FIREWORKS_API_KEY")
FIREWORKS_BASE_URL: str = _get("FIREWORKS_BASE_URL", "https://api.fireworks.ai/inference/v1")
FIREWORKS_MODEL: str = _get("FIREWORKS_MODEL", "accounts/fireworks/models/gemma-3-12b-it")

# AMD vLLM endpoint (OpenAI-compatible).
AMD_MODEL_ENDPOINT: str = _get("AMD_MODEL_ENDPOINT", "http://localhost:8000/v1")
AMD_MODEL_NAME: str = _get("AMD_MODEL_NAME", "flowforge")
AMD_MODEL_API_KEY: str = _get("AMD_MODEL_API_KEY", "EMPTY")

# n8n self-hosted management API.
N8N_API_URL: str = _get("N8N_API_URL", "http://localhost:5678/api/v1")
N8N_API_KEY: str = _get("N8N_API_KEY")
N8N_EDITOR_URL: str = _get("N8N_EDITOR_URL", "http://localhost:5678")
