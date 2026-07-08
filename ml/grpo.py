"""grpo.py — GRPO (RLVR) training on top of the SFT LoRA. Stretch goal.

Implemented in Prompt 9, only if time remains after SFT succeeds.

Unsloth GRPO trainer with a small group size (4) and low step count (100-200),
prompts sampled from data/out/train.jsonl, using reward.py as the reward signal.
Saves to a SEPARATE adapter (ml/outputs/grpo) so the SFT result is never
overwritten. Logs mean reward per step.
"""
from __future__ import annotations

SFT_ADAPTER = "ml/outputs"
GRPO_OUTPUT = "ml/outputs/grpo"

GROUP_SIZE = 4
MAX_STEPS = 200


def main() -> None:
    """TODO(Prompt 9): run Unsloth GRPO starting from the SFT LoRA."""
    raise NotImplementedError("grpo.py is implemented in Prompt 9 (stretch)")


if __name__ == "__main__":
    main()
