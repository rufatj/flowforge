"""FlowForge SFT entrypoint - RUNS ON AMD MI300X, NOT LOCALLY.

============================ MI300X / ROCm context ============================
Fresh AMD Developer Cloud droplet (ROCm PyTorch image), one-time setup:

    apt update && apt install python3.12-venv -y
    python3 -m venv unsloth_env && source unsloth_env/bin/activate
    pip install --upgrade torch==2.8.0 pytorch-triton-rocm torchvision torchaudio \
        torchao==0.13.0 xformers --index-url https://download.pytorch.org/whl/rocm6.4
    pip install --no-deps unsloth unsloth-zoo
    pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth"
    pip install datasets trl

Then, from the repo root:  python -m ml.finetune_sft

Notes: HSA_OVERRIDE_GFX_VERSION=9.4.2 makes ROCm treat the GPU as gfx942
(MI300X); Flash-Attention 2 is unavailable on ROCm so Unsloth falls back to
xformers; billing runs until the droplet is DESTROYED, so pull ml/outputs/
off the box and destroy it when done.
===============================================================================
"""
from __future__ import annotations

import os

# Must be set before torch/unsloth are imported anywhere.
os.environ.setdefault("HSA_OVERRIDE_GFX_VERSION", "9.4.2")
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ml.data_loader import build_dataset, heldout_prompts
from ml.model_setup import MAX_SEQ_LENGTH, attach_lora, load_model_and_tokenizer
from ml.train_config import ADAPTER_DIR, MERGED_DIR, build_sft_config


def smoke_test(model, tokenizer, n: int = 3) -> None:
    """Generate for a few heldout prompts so we see output quality immediately."""
    from ml.data_loader import load_chat_rows, HELDOUT_FILE  # system prompt source

    system = load_chat_rows(HELDOUT_FILE)[0]["messages"][0]["content"]
    for prompt in heldout_prompts(n):
        messages = [{"role": "system", "content": system}, {"role": "user", "content": prompt}]
        inputs = tokenizer.apply_chat_template(
            messages, tokenize=True, add_generation_prompt=True, return_tensors="pt"
        ).to(model.device)
        out = model.generate(input_ids=inputs, max_new_tokens=1024, temperature=0.2)
        text = tokenizer.decode(out[0][inputs.shape[1]:], skip_special_tokens=True)
        print(f"\n=== PROMPT: {prompt[:100]}\n{text[:500]}\n")


def main() -> None:
    from trl import SFTTrainer

    model, tokenizer, name = load_model_and_tokenizer()
    model = attach_lora(model)
    dataset = build_dataset(tokenizer)
    print(f"[train] {len(dataset)} examples, base={name}, max_seq_len={MAX_SEQ_LENGTH}")

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        args=build_sft_config(),
        max_seq_length=MAX_SEQ_LENGTH,
    )
    trainer.train()

    ADAPTER_DIR.mkdir(parents=True, exist_ok=True)
    MERGED_DIR.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(str(ADAPTER_DIR))
    tokenizer.save_pretrained(str(ADAPTER_DIR))
    model.save_pretrained_merged(str(MERGED_DIR), tokenizer, save_method="merged_16bit")
    print(f"[save] LoRA adapter -> {ADAPTER_DIR}\n[save] merged 16-bit -> {MERGED_DIR}")

    smoke_test(model, tokenizer)


if __name__ == "__main__":
    main()
