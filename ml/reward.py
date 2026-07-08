"""reward.py — verifiable reward function for GRPO (stretch goal).

Implemented in Prompt 9. reward(workflow_text) -> float:
  +0.2  valid JSON            (eval gate 1, local, no network)
  +0.3  schema valid          (eval gate 2, local, no network)
  +0.5  imports into local n8n (eval gate 3, with timeout; cap at 0.5 if n8n down)
  penalty for outputs over the length limit.

Reuses eval/harness.py gate functions so the reward and the benchmark measure the
exact same thing — this is what makes it RLVR (RL with verifiable rewards).
"""
from __future__ import annotations

MAX_LEN = 8192


def reward(workflow_text: str) -> float:
    """TODO(Prompt 9): score a generated workflow using the eval gates."""
    raise NotImplementedError("reward.py is implemented in Prompt 9")
