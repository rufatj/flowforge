<div align="center">

# ⚡ FlowForge

**Describe your automation in plain language. Get a working, importable n8n workflow.**

An open source, self hosted alternative to n8n's paid AI copilot, powered by **Gemma-3-4B**
fine tuned on real n8n workflows on an AMD Radeon PRO W7900. Your prompts never leave your infrastructure.

![License](https://img.shields.io/badge/license-MIT-black)
![Model](https://img.shields.io/badge/model-Gemma--3--4B%20LoRA-black)
![Hardware](https://img.shields.io/badge/fine--tuned%20on-AMD%20Radeon%20PRO%20W7900%20(gfx1100)-black)
![Training](https://img.shields.io/badge/training-transformers%20%2B%20PEFT-black)

</div>

---

## What it does

Type this:

> "When a customer sends a message on Instagram, classify their intent and if they want to buy something, add them to Google Sheets and notify me on Telegram."

FlowForge returns valid n8n workflow JSON: real node types, correct `typeVersion`s, and the
notoriously tricky double-nested `connections` wiring. One click imports it into your live n8n
instance. If the workflow starts with a webhook, you get an auto-generated test form to fire it
immediately.

## Why it exists

n8n's built-in AI assistant is paid, closed, and cloud-only. Your automation logic, data schemas,
and integration patterns all pass through someone else's servers. FlowForge inverts that: open
weights, open training data (public n8n community templates), MIT-licensed code, and inference on
hardware you control.

## Architecture

```
 frontend (React/Vite)  ──►  backend (FastAPI)  ──►  model endpoint (OpenAI-compatible)
        │                        │                      MODEL_MODE=fireworks  (dev)
        │                        │                      MODEL_MODE=amd        (vLLM on Radeon PRO W7900)
        │                        ▼
        └──────────────►  n8n instance (REST API import + webhook test forms)
```

**Data → model → proof pipeline:** 2,711 real community templates are collected and cleaned to
1,800 valid workflows, expanded to 5,400 chat pairs with LLM-rewritten natural-language requests,
split 85/15 by template id (no leakage between rewrites of the same workflow) into 4,590 train /
810 heldout, LoRA-fine-tuned into Gemma-3-4B on AMD hardware, and benchmarked by a three-gate
harness where the final gate is a **live n8n instance accepting the import** — not just a schema check.

| Folder | Concern |
|---|---|
| `data/` | Collect (api.n8n.io + HF dataset), clean, enrich (LLM prompt rewrites), split |
| `ml/` | LoRA SFT on AMD ROCm — `finetune_plain.py` (transformers.Trainer + PEFT, the path that works on gfx1100). `finetune_sft.py` is the Unsloth path (segfaults on RDNA3, see Lessons Learned) |
| `eval/` | Three-gate harness: JSON parse → schema check → **live n8n import**; `local_eval_plain.py` scores a model directly, `run_eval` benchmarks any OpenAI-compatible endpoint |
| `serving/` | vLLM launch script for the AMD GPU pod + a transformers FastAPI fallback |
| `backend/` | `/generate` (validate + one retry), `/import`, `/testform`, `/results` |
| `frontend/` | Landing, Generate, Result (import + live test form), Proof (benchmark numbers) |

## Quickstart

```bash
git clone <repo-url> flowforge && cd flowforge
cp .env.example .env          # set FIREWORKS_API_KEY (dev) or AMD_MODEL_ENDPOINT (self-hosted)
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend: http://localhost:8080/health
- n8n: http://localhost:5678 — first run: create an account, then **Settings → n8n API →
  Create an API key**, paste it into `.env` as `N8N_API_KEY`, and `docker compose restart backend`.

### Reproducing the dataset and benchmark

```bash
python data/collect.py                 # or data/collect_hf.py (2,737-template fallback)
python data/clean.py                   # sticky-note removal, allowlist filter, credential stubs
python data/enrich.py --limit 10       # smoke test first, then run full (needs FIREWORKS_API_KEY)
python data/enrich.py
python data/split.py                   # 85/15 by template id -> train.jsonl / heldout.jsonl

# on the GPU pod: train, then score base vs fine-tuned with the SAME settings
python3 -m ml.finetune_plain
python3 eval/local_eval_plain.py --model unsloth/gemma-3-4b-it \
  --label base-gemma-3-4b --limit 30 --out eval/results/eval_base_fixed.json
python3 eval/local_eval_plain.py --model ml/outputs/merged-gemma-flowforge \
  --label fine-tuned-gemma-3-4b --limit 30 --out eval/results/eval_ft_fixed.json
```

## Fine-tuning on AMD (Radeon PRO W7900)

bf16 LoRA (r=16, α=32, on `q/k/v/o/gate/up/down_proj`, gradient checkpointing) via plain
`transformers.Trainer` + PEFT — **not** Unsloth, which segfaults on this RDNA3 card (see
Lessons Learned). Base model `unsloth/gemma-3-4b-it`; 1 epoch, batch 1 × grad-accum 16,
`MAX_LEN=6144`, `adamw_torch`. Not QLoRA: bitsandbytes 4-bit is unstable on AMD.

Measured run: **269 steps, loss 1.43 → 0.90, 3 h 35 m** on a single Radeon PRO W7900
(gfx1100, RDNA3, 48 GB, ROCm 7.2.1, torch 2.10+rocm7.1). Of the 4,590 train rows, 4,297 fit
under the 6,144-token limit; the rest are dropped rather than truncated mid-JSON.

```bash
# on the GPU pod
python3 -m ml.finetune_plain        # saves merged bf16 model to ml/outputs/merged-gemma-flowforge
bash serving/serve_vllm.sh          # OpenAI-compatible endpoint on :8000
```

Point the app at it: `MODEL_MODE=amd`, `AMD_MODEL_ENDPOINT=http://<pod>:8000/v1`
(or an SSH tunnel: `ssh -L 8000:localhost:8000 root@<pod>`).

## Results

30 held-out prompts (workflows never seen in training), **identical harness and generation
settings for both models**: greedy, `repetition_penalty=1.1`, `no_repeat_ngram_size=6`,
`max_new_tokens=6144`. Gate 1 = output parses as JSON; Gate 2 = it is a structurally valid n8n
workflow (non-empty `nodes` array, `connections` object, every node has `name` + `type`).

| Run | Gate 1 · JSON valid | Gate 2 · Schema valid |
|---|---|---|
| Base `gemma-3-4b-it` (before) | 0.0% | 0.0% |
| **FlowForge LoRA (after)** | **20.0%** | **20.0%** |

Raw results: [`eval/results/eval_base_fixed.json`](eval/results/eval_base_fixed.json) ·
[`eval/results/eval_ft_fixed.json`](eval/results/eval_ft_fixed.json).

**What the numbers mean, honestly:**

- **Base model: 0%.** Off-the-shelf Gemma-3-4B produces zero valid n8n workflows — it doesn't
  know the node types, the `typeVersion`s, or the double-nested `connections` wiring. Fine-tuning
  is what makes the task possible at all, not just better.
- **Gate 1 == Gate 2 for the fine-tuned model.** Every time it emits parseable JSON, that JSON is
  *always* a schema-valid n8n workflow. The model learned the structure; it does not emit
  malformed-but-parseable objects. So the entire gap to 100% is **not wrong schema** — it is
  **unterminated JSON on the longest workflows**: generation is cut off mid-string on the biggest
  outputs before the closing braces, failing the JSON parse. Shorter and mid-size workflows
  succeed cleanly.
- **Gate 3 (live n8n import) is not in this table.** The GPU pod cannot reach the n8n instance
  (it runs on a separate machine), so the before/after model comparison covers gates 1–2 only.
  Gate 3 itself is validated separately: running the *ground-truth training targets* through the
  live-import gate on a local n8n scores 100% JSON / 96.7% schema / 100% import of schema-valid
  examples (n=30) — so the harness and the import path are proven; only the pod's network
  isolation kept it out of this run.

The immediate path to raising the 20%: higher generation budget for the largest workflows and a
second epoch (loss was still falling cleanly at 0.90). See Lessons Learned for the truncation trap.

## Known Issues / Lessons Learned

Two findings we could not find documented anywhere, learned the hard (GPU-hour-burning) way:

### 1. Gemma-4 cannot currently be LoRA-fine-tuned on this stack

`unsloth/gemma-4-E4B-it` was our first choice (newest Gemma, small enough for 48 GB). It does not
work with either fine-tuning path available on an RDNA3 card:

- **PEFT**: Gemma-4's `Gemma4ClippableLinear` layers are not in PEFT's supported-module list, so
  `get_peft_model` cannot attach LoRA adapters to them.
- **Unsloth**: `FastModel`'s optimized path **segfaults on gfx1100 (RDNA3)** — Unsloth's AMD
  support is built and tested for CDNA (MI-series), not RDNA workstation cards.

We fell back to **Gemma-3-4B + plain `transformers.Trainer` + PEFT LoRA**, which works on this
card. Gemma-3 is still Gemma (prize-track intact) and is fully supported by PEFT's LoRA modules.
If you are on an RDNA3 workstation GPU, start here — do not burn hours on Gemma-4 or Unsloth.

### 2. The sequence-length trap (this cost us a full training run)

n8n workflow JSON is **long**. On our dataset the token-length distribution is:

| median | p90 | p99 |
|---|---|---|
| 3,102 | 5,375 | 7,332 |

Our first run used `max_len=2048`. That **truncated 78% of examples mid-JSON.** The model
therefore *never saw a single terminated workflow*, never learned to emit the EOS token, and at
inference looped forever — generating duplicate nodes until it hit the token cap. Gate 1 was 3.3%.

Raising `max_len` to **6,144** (covers the median and p90, drops only the p99 tail rather than
truncating it) fixed it: the model finally saw complete workflows ending in EOS, and Gate 1 rose
to 20% with the remaining failures being *only* the longest outputs.

**Measure your dataset's token lengths BEFORE training** — this check is free and takes seconds,
versus a wasted multi-hour run:

```python
# token-length distribution of your training targets — run before you pick max_len
import json, statistics
from transformers import AutoTokenizer

tok = AutoTokenizer.from_pretrained("unsloth/gemma-3-4b-it")
lens = []
with open("data/out/train.jsonl", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        msgs = json.loads(line)["messages"]
        # tokenize the full rendered conversation exactly as training will
        ids = tok.apply_chat_template(msgs, add_generation_prompt=False, tokenize=True)
        ids = ids.input_ids if hasattr(ids, "input_ids") else ids
        lens.append(len(ids[0]) if ids and isinstance(ids[0], list) else len(ids))

lens.sort()
p = lambda q: lens[int(len(lens) * q)]
print(f"n={len(lens)}  median={statistics.median(lens):.0f}  "
      f"p90={p(0.90)}  p99={p(0.99)}  max={lens[-1]}")
print(f"truncated at max_len=2048: {sum(l > 2048 for l in lens) / len(lens):.0%}")
print(f"truncated at max_len=6144: {sum(l > 6144 for l in lens) / len(lens):.0%}")
```

If a large fraction exceeds your `max_len`, either raise it or **drop** the over-length examples —
never let the trainer truncate them, or you teach the model that workflows have no end.

> Exact percentiles shift a little with tokenizer/transformers version and with a couple of
> outlier templates, but the conclusion is stable: the large majority of examples exceed 2,048
> tokens, and only ~6% exceed 6,144 (that's why 4,297 of 4,590 train rows are kept). Measure on
> the same versions you'll train with.

## Prior art

FlowForge builds on and differentiates from earlier n8n-generation work: mbakgun's
Qwen3-Coder fine-tune and 2,737-template dataset, Nishan30's TypeScript-DSL approach,
MustaphaL's Llama 3 fine-tune, and czlonkowski/n8n-mcp's node database and validator.
Differences: AMD ROCm + Gemma, a live-import evaluation gate (not just schema checks),
and a complete self-hosted product around the model.

## License

MIT — see [LICENSE](LICENSE). Community templates used in training remain the property of
their original creators.
