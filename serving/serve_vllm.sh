#!/usr/bin/env bash
# serve_vllm.sh — serve the merged FlowForge model with vLLM on the AMD GPU pod.
#
# Target GPU: Radeon PRO W7900 (RDNA3, gfx1100, 48 GB VRAM) — NOT an MI300X.
# gfx1100 is natively supported by ROCm; do NOT set HSA_OVERRIDE_GFX_VERSION.
# A 12B model in bf16 (~24 GB) fits at TP=1 with room for KV cache.
#
# *** UNVERIFIED ON gfx1100 — check before relying on this: ***
# The docker image below (vllm/vllm-openai-rocm:gemma4) was chosen for MI300X;
# official ROCm vLLM images are typically built for CDNA targets (gfx90a/gfx942)
# and may not ship gfx1100 kernels. If the container crashes on startup with an
# unsupported-arch / HIP error:
#   1. try a nightly image built with RDNA3 support (e.g. rocm/vllm-dev), or
#      build vLLM from source with GPU_ARCHS=gfx1100, or
#   2. skip vLLM entirely and use the transformers fallback (same OpenAI API):
#         python serving/serve_fallback.py --model "$MODEL_PATH" --port 8000
#
# Prereqs on the pod: ROCm, docker, and the merged model in ml/outputs/.
set -euo pipefail

MODEL_PATH="${MODEL_PATH:-/workspace/flowforge/ml/outputs/merged-gemma-flowforge}"
SERVED_NAME="${SERVED_NAME:-flowforge}"
PORT="${PORT:-8000}"
API_KEY="${API_KEY:-changeme}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-8192}"

docker pull vllm/vllm-openai-rocm:gemma4

docker run -itd --name flowforge-vllm --ipc=host --network=host --privileged \
  --device=/dev/kfd --device=/dev/dri --group-add=video \
  --security-opt seccomp=unconfined --shm-size 16G \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  -v "$(dirname "$MODEL_PATH")":"$(dirname "$MODEL_PATH")" \
  vllm/vllm-openai-rocm:gemma4 \
  --model "$MODEL_PATH" \
  --served-model-name "$SERVED_NAME" \
  --host 0.0.0.0 --port "$PORT" \
  --gpu-memory-utilization 0.90 \
  --max-model-len "$MAX_MODEL_LEN" \
  --limit-mm-per-prompt image=0,audio=0 \
  --api-key "$API_KEY"

echo "vLLM starting on :$PORT (served-model-name=$SERVED_NAME)."
echo "Point the backend at it:  AMD_MODEL_ENDPOINT=http://<host>:$PORT/v1"
echo "Or tunnel securely:       ssh -L 8000:localhost:$PORT root@<droplet-ip>"
