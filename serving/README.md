# Serving FlowForge on AMD MI300X

Exact commands to serve the fine-tuned model on a fresh MI300X droplet.
Fully expanded in Prompt 8; this is the reference for the demo/judging path.

## Option A — vLLM (preferred)

```bash
# on the MI300X droplet, after merging the model into ml/outputs/
MODEL_PATH=/path/to/merged-gemma-flowforge \
SERVED_NAME=flowforge \
API_KEY=<strong-key> \
bash serving/serve_vllm.sh
```

The endpoint is OpenAI-compatible at `http://<host>:8000/v1`. The request `model`
field must equal `--served-model-name` (`flowforge`).

## Option B — transformers fallback

If vLLM + ROCm fights you:

```bash
HSA_OVERRIDE_GFX_VERSION=9.4.2 \
python serving/serve_fallback.py --model ml/outputs/merged-gemma-flowforge --port 8000
```

## Pointing the app at it

- **SSH tunnel (most secure):** `ssh -L 8000:localhost:8000 root@<droplet-ip>`,
  then set `AMD_MODEL_ENDPOINT=http://localhost:8000/v1` and `MODEL_MODE=amd`.
- **Open port + key:** set `AMD_MODEL_ENDPOINT=http://<droplet-ip>:8000/v1` and
  `AMD_MODEL_API_KEY=<key>`. Destroy the droplet after the demo.

## Credit discipline

At $1.99/GPU-hr, $100 ≈ 50 hours. Spin up for the demo, tear down after — a
powered-off instance is still billed; charges stop only on **destroy**.
