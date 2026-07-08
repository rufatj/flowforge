"""Model client — routes generation to the right OpenAI-compatible endpoint.

MODEL_MODE decides the backend:
  - "fireworks" -> https://api.fireworks.ai/inference/v1  (development / base model)
  - "amd"       -> AMD_MODEL_ENDPOINT (your vLLM server on MI300X, demo/judging)

Both are OpenAI-compatible, so the same openai python client works for both;
only base_url / api_key / model change. Route logic elsewhere never needs to
know which mode is active.
"""
from __future__ import annotations

from functools import lru_cache

from openai import OpenAI

from app import config
from app.prompts import SYSTEM_PROMPT


@lru_cache(maxsize=1)
def _client_and_model() -> tuple[OpenAI, str]:
    """Build the OpenAI client + model name for the active MODEL_MODE."""
    if config.MODEL_MODE == "amd":
        client = OpenAI(
            base_url=config.AMD_MODEL_ENDPOINT,
            api_key=config.AMD_MODEL_API_KEY or "EMPTY",
        )
        return client, config.AMD_MODEL_NAME

    # Default: fireworks.
    client = OpenAI(
        base_url=config.FIREWORKS_BASE_URL,
        api_key=config.FIREWORKS_API_KEY or "EMPTY",
    )
    return client, config.FIREWORKS_MODEL


def active_mode() -> str:
    """Return the currently selected model mode (for /health and diagnostics)."""
    return config.MODEL_MODE


def generate_workflow(description: str, *, extra_reminder: str | None = None) -> str:
    """Ask the model for a workflow JSON string for the given description.

    NOTE (stub): full behaviour (JSON validation + one stricter retry) is
    implemented in Prompt 5. For the skeleton this issues a single chat
    completion so the wiring is real and testable once a key is set.
    """
    client, model = _client_and_model()

    user_content = description
    if extra_reminder:
        user_content = f"{description}\n\n{extra_reminder}"

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.2,
        max_tokens=4096,
    )
    return response.choices[0].message.content or ""
