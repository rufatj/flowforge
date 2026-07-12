"""SFT training arguments for the MI300X run.

Effective batch = PER_DEVICE_BATCH x GRAD_ACCUM = 16. If the box OOMs at
seq len 8192 (long workflow JSONs), halve PER_DEVICE_BATCH and double
GRAD_ACCUM - same effective batch, same result, slower wall clock.

Loss sanity (from Unsloth's Gemma guide): 1-3 is normal for a 12B dense
model; 100+ means the (long-fixed) gradient-accumulation bug - update Unsloth.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / "ml" / "outputs"
ADAPTER_DIR = OUTPUT_DIR / "lora_adapter"
MERGED_DIR = OUTPUT_DIR / "merged-gemma-flowforge"

EPOCHS = 2
LEARNING_RATE = 2e-4
PER_DEVICE_BATCH = 4
GRAD_ACCUM = 4
WARMUP_RATIO = 0.03
LOGGING_STEPS = 10


def build_sft_config():
    """TRL SFTConfig, deferred import so this file parses without trl installed."""
    from trl import SFTConfig

    return SFTConfig(
        output_dir=str(OUTPUT_DIR / "checkpoints"),
        num_train_epochs=EPOCHS,
        learning_rate=LEARNING_RATE,
        lr_scheduler_type="cosine",
        warmup_ratio=WARMUP_RATIO,
        per_device_train_batch_size=PER_DEVICE_BATCH,
        gradient_accumulation_steps=GRAD_ACCUM,
        logging_steps=LOGGING_STEPS,
        save_strategy="steps", save_steps=50, save_total_limit=2,
        bf16=True,
        optim="adamw_8bit",
        weight_decay=0.01,
        seed=42,
        report_to="none",
        dataset_text_field="text",
    )
