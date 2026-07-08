<div align="center">

# ⚡ FlowForge

**Describe your automation in plain language. Get a working, importable n8n workflow.**

An open source, self hosted alternative to n8n's paid AI copilot, powered by a Gemma model
fine tuned on thousands of real workflows on an AMD MI300X. Your prompts never leave your infrastructure.

![License](https://img.shields.io/badge/license-MIT-black)
![Model](https://img.shields.io/badge/model-Gemma%2012B%20LoRA-black)
![Hardware](https://img.shields.io/badge/fine--tuned%20on-AMD%20MI300X-black)
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
        │                        │                      MODEL_MODE=amd        (vLLM on MI300X)
        │                        ▼
        └──────────────►  n8n instance (REST API import + webhook test forms)
```

| Folder | Concern |
|---|---|
| `data/` | Collect (api.n8n.io + HF dataset), clean, enrich (LLM prompt rewrites), split |
| `ml/` | Unsloth 16-bit LoRA SFT on MI300X: `data_loader` / `model_setup` / `train_config` / `finetune_sft` |
| `eval/` | Three-gate harness: JSON parse → schema check → **live n8n import**; `run_eval` benchmarks any endpoint |
| `serving/` | vLLM launch script for MI300X + a transformers FastAPI fallback |
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

## Fine-tuning on AMD MI300X

16-bit LoRA (r=16, α=32, attention+MLP projections, gradient checkpointing, bf16) with
[Unsloth](https://github.com/unslothai/unsloth) on a single MI300X (192 GB, ROCm). Not QLoRA:
bitsandbytes 4-bit is unstable on AMD and unnecessary at this scale. Training data is ~1,800
cleaned community workflows expanded to ~5,000 chat pairs via LLM-rewritten natural-language
requests.

```bash
# on the MI300X droplet (setup commands in ml/finetune_sft.py header)
python -m ml.finetune_sft            # saves LoRA adapter + merged 16-bit model to ml/outputs/
bash serving/serve_vllm.sh           # OpenAI-compatible endpoint on :8000
```

Point the app at it: `MODEL_MODE=amd`, `AMD_MODEL_ENDPOINT=http://<droplet>:8000/v1`
(or an SSH tunnel: `ssh -L 8000:localhost:8000 root@<droplet>`).

## Results

Measured by the three-gate harness on a held-out set of real workflow requests
(never seen in training). Gate 3 = a live n8n instance accepts the import.

| Run | JSON valid | Schema valid | Live import |
|---|---|---|---|
| Base Gemma (before) | _pending_ | _pending_ | _pending_ |
| FlowForge SFT (after) | _pending_ | _pending_ | _pending_ |

> Numbers are produced by `eval/run_eval.py` and land in `eval/results/results.json`;
> the Proof page renders them live. Baseline runs before fine-tuning; the SFT row is
> filled after the MI300X training run.

## Prior art

FlowForge builds on and differentiates from earlier n8n-generation work: mbakgun's
Qwen3-Coder fine-tune and 2,737-template dataset, Nishan30's TypeScript-DSL approach,
MustaphaL's Llama 3 fine-tune, and czlonkowski/n8n-mcp's node database and validator.
Differences: AMD MI300X + Gemma, a live-import evaluation gate (not just schema checks),
and a complete self-hosted product around the model.

## License

MIT — see [LICENSE](LICENSE). Community templates used in training remain the property of
their original creators.
