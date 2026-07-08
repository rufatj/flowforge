"""Load the base Gemma model with Unsloth and attach LoRA adapters.

Runs on AMD MI300X (ROCm). 16-bit LoRA, NOT QLoRA: bitsandbytes 4-bit is
unstable on AMD (Unsloth auto-disables it) and the 192 GB card fits a 12B
model in bf16 with room to spare.

Fallback chain: if gemma-4-12b-it fights Unsloth on ROCm for more than a few
hours, switch to gemma-3-12b-it (mature ROCm support, still Gemma so the
Gemma prize track is preserved). Just reorder MODEL_CANDIDATES.
"""
from __future__ import annotations

MODEL_CANDIDATES = [
    "unsloth/gemma-4-12b-it",   # primary target
    "unsloth/gemma-3-12b-it",   # proven fallback on ROCm
]

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

    candidates = [model_name] if model_name else MODEL_CANDIDATES
    last_error: Exception | None = None
    for name in candidates:
        try:
            model, tokenizer = FastModel.from_pretrained(
                model_name=name,
                max_seq_length=MAX_SEQ_LENGTH,
                load_in_4bit=False,          # 16-bit LoRA on MI300X
                dtype=None,                  # auto -> bf16 on MI300X
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
