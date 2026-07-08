"""OpenAI-compatible generation call used by run_eval.

Works against any /v1/chat/completions endpoint: Fireworks (baseline), the
AMD MI300X vLLM server (fine-tuned), or a local stub during testing.
"""
from __future__ import annotations

import time

from openai import OpenAI

# The system prompt must match training exactly (data/split.py).
SYSTEM_PROMPT = (
    "You are FlowForge, an expert n8n workflow generator. Given a natural "
    "language description of an automation, return ONLY valid n8n workflow "
    "JSON with a nodes array and connections object. Do not include sticky "
    "notes, explanations, markdown, or any text outside the JSON."
)

MAX_RETRIES = 3


class ModelEndpoint:
    def __init__(self, base_url: str, model: str, api_key: str = "EMPTY",
                 max_tokens: int = 4096, temperature: float = 0.2) -> None:
        self.client = OpenAI(base_url=base_url, api_key=api_key or "EMPTY")
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    def generate(self, description: str) -> str:
        """One workflow generation; retries transient failures with backoff."""
        last_error: Exception | None = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": description},
                    ],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                )
                return resp.choices[0].message.content or ""
            except Exception as e:  # noqa: BLE001 - any transport error retries
                last_error = e
                time.sleep(2 * attempt)
        raise RuntimeError(f"generation failed after {MAX_RETRIES} attempts: {last_error}")
