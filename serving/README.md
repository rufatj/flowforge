# Serving FlowForge on the AMD GPU pod (Radeon PRO W7900)

Exact commands to serve the fine-tuned model on the pod. Target GPU is a
Radeon PRO W7900 — RDNA3, gfx1100, 48 GB VRAM. gfx1100 is natively supported
by ROCm: do NOT set HSA_OVERRIDE_GFX_VERSION (the old 9.4.2 value spoofed an
MI300X and breaks RDNA3). This is the reference for the demo/judging path.

## Option A — vLLM (preferred)

```bash
# on the pod, after merging the model into ml/outputs/
MODEL_PATH=/path/to/merged-gemma-flowforge \
SERVED_NAME=flowforge \
API_KEY=<strong-key> \
bash serving/serve_vllm.sh
```

The endpoint is OpenAI-compatible at `http://<host>:8000/v1`. The request `model`
field must equal `--served-model-name` (`flowforge`).

**gfx1100 caveat:** the docker image in `serve_vllm.sh` was picked for MI300X and may
lack RDNA3 kernels — see the UNVERIFIED note at the top of that script. If it fails,
use Option B; it works anywhere ROCm torch does.

## Option B — transformers fallback

If vLLM + ROCm fights you:

```bash
python serving/serve_fallback.py --model ml/outputs/merged-gemma-flowforge --port 8000
```

## Pointing the app at it

- **SSH tunnel (most secure):** `ssh -L 8000:localhost:8000 root@<pod-ip>`,
  then set `AMD_MODEL_ENDPOINT=http://localhost:8000/v1` and `MODEL_MODE=amd`.
- **Open port + key:** set `AMD_MODEL_ENDPOINT=http://<pod-ip>:8000/v1` and
  `AMD_MODEL_API_KEY=<key>`. Destroy the pod after the demo.

## Credit discipline

At $1.99/GPU-hr, $100 ≈ 50 hours. Spin up for the demo, tear down after — a
powered-off instance is still billed; charges stop only on **destroy**.
