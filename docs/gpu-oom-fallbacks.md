# W7900 (48 GB) — model sizing math & OOM decision table

Target card: Radeon PRO W7900 — RDNA3, gfx1100, **48 GB VRAM**.
Single switch: `MODEL_NAME` at the top of `ml/model_setup.py`, or
`FLOWFORGE_BASE_MODEL=<hf-id> python -m ml.finetune_sft` (no code edit).

## VRAM math (16-bit LoRA, seq 8192, batch 2, grad-accum 8, checkpointing, adamw_8bit)

### 12B Gemma (`unsloth/gemma-4-12b-it`) — the honest picture

| Component | Estimate | Notes |
|---|---|---|
| Weights, bf16 | ~24 GB | 12B × 2 bytes; frozen (LoRA) but resident |
| LoRA adapters r=16 (+grads +8-bit Adam) | ~0.6 GB | ~80–100M trainable params over attn+MLP |
| Checkpointed activations | ~6 GB | batch 2 × seq 8192 × hidden ~3840 × ~48 layers × 2 B |
| Attention recompute workspace | 1–3 GB *(good path)* / much worse *(naive fallback)* | depends on memory-efficient attention having gfx1100 kernels |
| LM-head logits + CE over Gemma's **262k vocab** | 2–4 GB *(chunked)* / **~9–17 GB (unchunked)** | the classic Gemma OOM; batch 2 × 8192 × 262144 × 2 B ≈ 8.6 GB bf16, ~2× if upcast to fp32 |
| HIP runtime + fragmentation | 2–4 GB | |
| **Peak** | **~35 GB best case — but ~50+ GB if ONE optimized kernel path is missing on RDNA3** | |

Verdict: 12B *can* fit, but only if Unsloth's chunked cross-entropy **and**
memory-efficient attention both work on gfx1100 — exactly the parts that are
unverified on RDNA3. That makes 12B a **stretch goal**, not the primary.

### 4B-class Gemma (`unsloth/gemma-4-E4B-it`, primary) 

| Component | Estimate |
|---|---|
| Weights, bf16 | ~8–9 GB |
| LoRA + optimizer | ~0.4 GB |
| Checkpointed activations (same settings) | ~2–3 GB |
| Logits/CE + recompute + runtime | ~4–6 GB even on unoptimized paths |
| **Peak** | **~15–20 GB — comfortable; survives kernel fallbacks** |

This is also the model class the official AMD Unsloth playbook demonstrates on
workstation cards, and it is still Gemma (prize track preserved).

## Decision table — exact moves, in order

| # | Symptom | Change exactly this | Where |
|---|---|---|---|
| 1 | OOM (any point) on the default run | Nothing to lower — you're already on the 4B primary. Go to row 2. | — |
| 2 | OOM during a training step (4B) | `PER_DEVICE_BATCH = 2` → `1`, `GRAD_ACCUM = 8` → `16` | `ml/train_config.py` |
| 3 | Still OOM (4B, batch 1) | `MAX_SEQ_LENGTH = 8192` → `4096` (avg example ≈ 2.5k tokens, so few truncate) | `ml/model_setup.py` |
| 4 | Unsloth crashes on gfx1100 (arch/kernel error, NOT OOM) | Drop Unsloth: plain `trl` + `peft` LoRA, same dataset/config (`SFTTrainer` works with any HF model) | new small script; same `train_config` values |
| 5 | `gemma-4-E4B-it` won't download/load (auth/gated) | Auto-falls back to `unsloth/gemma-3-4b-it` (already wired) | nothing to do |
| 6 | 4B run finished, time + VRAM allow a stretch | `FLOWFORGE_BASE_MODEL=unsloth/gemma-4-12b-it` **and** row 2 changes **and** row 3 change, all pre-emptively | env var + both files |
| 7 | 12B stretch OOMs anyway | Abandon 12B, ship the 4B result — it's already benchmarked | — |

## Serving note

For **inference** (vLLM / serve_fallback), 12B bf16 ≈ 24 GB weights + KV cache
fits fine in 48 GB — serving is not the constraint; training is.
