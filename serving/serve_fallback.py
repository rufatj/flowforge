"""Fallback server for MI300X: transformers + FastAPI, OpenAI-compatible.

Use ONLY if vLLM misbehaves on ROCm. Exposes POST /v1/chat/completions with
just enough of the OpenAI schema for backend/app/model_client.py and
eval/run_eval.py to work unchanged (MODEL_MODE=amd pointed at this port).

On the droplet:
        --model ml/outputs/merged-gemma-flowforge --port 8000
"""
from __future__ import annotations

import argparse
import os
import time


from fastapi import FastAPI
from pydantic import BaseModel


class ChatRequest(BaseModel):
    model: str = "flowforge"
    messages: list[dict]
    max_tokens: int = 4096
    temperature: float = 0.2


def build_app(generate_fn) -> FastAPI:
    """generate_fn(messages, max_tokens, temperature) -> str. Injected for testability."""
    app = FastAPI(title="FlowForge fallback server")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.post("/v1/chat/completions")
    def chat(req: ChatRequest):
        text = generate_fn(req.messages, req.max_tokens, req.temperature)
        return {
            "id": f"chatcmpl-{int(time.time()*1000)}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": req.model,
            "choices": [{"index": 0, "finish_reason": "stop",
                         "message": {"role": "assistant", "content": text}}],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        }

    return app


def hf_generate_fn(model_path: str):
    """Real generator: loads the merged model with transformers (ROCm torch)."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(
        model_path, torch_dtype=torch.bfloat16, device_map="auto"
    )

    def generate(messages: list[dict], max_tokens: int, temperature: float) -> str:
        inputs = tokenizer.apply_chat_template(
            messages, tokenize=True, add_generation_prompt=True, return_tensors="pt"
        ).to(model.device)
        out = model.generate(
            input_ids=inputs, max_new_tokens=max_tokens,
            temperature=max(temperature, 0.01), do_sample=temperature > 0,
        )
        return tokenizer.decode(out[0][inputs.shape[1]:], skip_special_tokens=True)

    return generate


def main() -> None:
    import uvicorn

    p = argparse.ArgumentParser()
    p.add_argument("--model", default="ml/outputs/merged-gemma-flowforge")
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--host", default="0.0.0.0")
    args = p.parse_args()

    app = build_app(hf_generate_fn(args.model))
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
