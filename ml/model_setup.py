"""Load the base Gemma model with Unsloth and attach LoRA adapters.

Runs on the AMD GPU pod: Radeon PRO W7900 (RDNA3, gfx1100, 48 GB VRAM).
16-bit LoRA, NOT QLoRA: bitsandbytes 4-bit is unstable on AMD (Unsloth
auto-disables it).

Model sizing for 48 GB (see docs/gpu-oom-fallbacks.md for the full math):
a 4B-class Gemma peaks at ~15-20 GB here — comfortable even if RDNA3 kernel
fallbacks bite. A 12B Gemma is ~24 GB of weights alone and only fits if
EVERY optimization works on gfx1100 (memory-efficient attention + chunked
cross-entropy over Gemma's 262k vocab); one fallback path blows past 48 GB.
So 4B is the primary and 12B is a manual stretch goal, never an auto-fallback.

MODEL_NAME below is the single switch. On the pod you can also override
without editing code:  FLOWFORGE_BASE_MODEL=unsloth/gemma-4-12b-it python -m ml.finetune_sft
"""
from __future__ import annotations

import os

# ---- SINGLE SWITCH: change this line (or set FLOWFORGE_BASE_MODEL) ---------
# Primary: the model the official AMD Unsloth playbook uses on workstation
# cards — 4B-class, instruction-tuned, still Gemma (prize track preserved).
MODEL_NAME = os.environ.get("FLOWFORGE_BASE_MODEL", "unsloth/gemma-4-E4B-it")

# Tried in order ONLY if MODEL_NAME fails to LOAD (auth/gated/download issues,
# not OOM). Same 4B class on purpose: auto-falling "up" to 12B would just OOM.
FALLBACK_CANDIDATES = [
    "unsloth/gemma-3-4b-it",    # mature ROCm support, same size class
]

# Manual stretch option, NOT in the auto-fallback chain: unsloth/gemma-4-12b-it
# — only try it after a 4B run is safely finished, with PER_DEVICE_BATCH=1,
# GRAD_ACCUM=16 and ideally MAX_SEQ_LENGTH=4096 (decision table in
# docs/gpu-oom-fallbacks.md).

MAX_SEQ_LENGTH = 8192   # workflow JSON is long
LORA_R = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.0
TARGET_MODULES = [       # attention + MLP projections
    "q_proj", "k_proj", "v_proj", "o_proj",
    "gate_proj", "up_proj", "down_proj",
]


def load_model_and_tokenizer(model_name: str | None = None):
    """Try each candidate until one loads; returns (model, tokenizer, name)."""
    from unsloth import FastModel  # deferred: only exists on the GPU box

    candidates = [model_name] if model_name else [MODEL_NAME, *FALLBACK_CANDIDATES]
    last_error: Exception | None = None
    for name in candidates:
        try:
            model, tokenizer = FastModel.from_pretrained(
                model_name=name,
                max_seq_length=MAX_SEQ_LENGTH,
                load_in_4bit=False,          # 16-bit LoRA (bnb 4-bit unstable on AMD)
                dtype=None,                  # auto -> bf16 on ROCm
            )
            print(f"[model_setup] loaded {name}")
            return model, tokenizer, name
        except Exception as e:  # noqa: BLE001 - fall through to the next candidate
            print(f"[model_setup] {name} failed: {e}")
            last_error = e
    raise RuntimeError(f"no base model could be loaded: {last_error}")


def attach_lora(model):
    from unsloth import FastModel

    return FastModel.get_peft_model(
        model,
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        target_modules=TARGET_MODULES,
        use_gradient_checkpointing="unsloth",
        random_state=42,
    )
