#!/usr/bin/env bash
# serve_vllm.sh — serve the merged FlowForge model with vLLM on AMD MI300X.
#
# Fleshed out in Prompt 8. Launches the OpenAI-compatible vLLM server on port
# 8000 so the backend (MODEL_MODE=amd) can call it. The 12B model fits on a
# single MI300X at TP=1 with full context.
#
# Prereqs on the droplet: ROCm, docker, and the merged model in ml/outputs/.
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
