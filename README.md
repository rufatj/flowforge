<div align="center">

# ⚡ FlowForge

**Describe your automation in plain language. Get a working, importable n8n workflow.**

An open source, self hosted alternative to n8n's paid AI copilot, powered by a Gemma model
fine tuned on thousands of real workflows on an AMD Radeon PRO W7900. Your prompts never leave your infrastructure.

![License](https://img.shields.io/badge/license-MIT-black)
![Model](https://img.shields.io/badge/model-Gemma%20LoRA-black)
![Hardware](https://img.shields.io/badge/fine--tuned%20on-AMD%20Radeon%20PRO%20W7900-black)
![Serving](https://img.shields.io/badge/serving-vLLM-black)

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

**Data → model → proof pipeline:** 1,800 real community workflows are collected and cleaned,
expanded to 5,400 chat pairs with LLM-rewritten natural-language requests, split 85/15 by
template id (no leakage between rewrites of the same workflow), LoRA-fine-tuned into Gemma on
AMD hardware, and benchmarked by a three-gate harness where the final gate is a **live n8n
instance accepting the import** — not just a schema check.

| Folder | Concern |
|---|---|
| `data/` | Collect (api.n8n.io + HF dataset), clean, enrich (LLM prompt rewrites), split |
| `ml/` | Unsloth 16-bit LoRA SFT on AMD ROCm: `data_loader` / `model_setup` / `train_config` / `finetune_sft` |
| `eval/` | Three-gate harness: JSON parse → schema check → **live n8n import**; `run_eval` benchmarks any endpoint |
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

python -m eval.run_eval --label base-gemma \
  --base-url https://api.fireworks.ai/inference/v1 \
  --model "$FIREWORKS_MODEL" --api-key "$FIREWORKS_API_KEY" --limit 10   # then full run
```

## Fine-tuning on AMD (Radeon PRO W7900)

16-bit LoRA (r=16, α=32, attention+MLP projections, gradient checkpointing, bf16) with
[Unsloth](https://github.com/unslothai/unsloth) on a single Radeon PRO W7900 (RDNA3 gfx1100,
48 GB, ROCm). Not QLoRA: bitsandbytes 4-bit is unstable on AMD and unnecessary at this scale.
Training data is 1,800 cleaned community workflows expanded to 5,400 chat pairs via
LLM-rewritten natural-language requests.

```bash
# on the GPU pod (setup commands in ml/finetune_sft.py header)
python -m ml.finetune_sft            # saves LoRA adapter + merged 16-bit model to ml/outputs/
bash serving/serve_vllm.sh           # OpenAI-compatible endpoint on :8000
```

Point the app at it: `MODEL_MODE=amd`, `AMD_MODEL_ENDPOINT=http://<pod>:8000/v1`
(or an SSH tunnel: `ssh -L 8000:localhost:8000 root@<pod>`).

## Results

Measured by the three-gate harness on 810 held-out prompts (270 workflows never seen in
training, incl. their rewrites). Gate 3 = a **live n8n instance accepts the import** via
REST API — the strictest possible correctness check short of executing the workflow.

| Run | Gate 1 · JSON valid | Gate 2 · Schema valid | Gate 3 · Live import |
|---|---|---|---|
| Base Gemma (before fine-tuning) | \_\_\_% | \_\_\_% | \_\_\_% |
| **FlowForge SFT (after)** | **\_\_\_%** | **\_\_\_%** | **\_\_\_%** |

**Data quality floor (ground truth):** running the *training targets themselves* through the
same three gates scores 100% JSON / 96.7% schema / 100% live-import of schema-valid examples
(n=30 random held-out ground truths) — so the benchmark ceiling is real and the gates measure
model quality, not dataset noise.

> Both rows come from one command once both endpoints are up:
> `python -m eval.compare_before_after --base-url <URL> --base-model <ID> --ft-url <URL> --ft-model flowforge`
> which writes `eval/results/comparison.json` and prints this table. The Proof page renders
> `eval/results/results.json` live.

## Prior art

FlowForge builds on and differentiates from earlier n8n-generation work: mbakgun's
Qwen3-Coder fine-tune and 2,737-template dataset, Nishan30's TypeScript-DSL approach,
MustaphaL's Llama 3 fine-tune, and czlonkowski/n8n-mcp's node database and validator.
Differences: AMD ROCm + Gemma, a live-import evaluation gate (not just schema checks),
and a complete self-hosted product around the model.

## License

MIT — see [LICENSE](LICENSE). Community templates used in training remain the property of
their original creators.
