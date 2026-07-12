#!/usr/bin/env bash
# =============================================================================
# FlowForge unattended SFT pipeline — AMD Radeon PRO W7900 pod (gfx1100, 48 GB)
#
# Run from a Jupyter terminal:
#     cd /workspace/flowforge && bash run_pipeline.sh
#
# Everything is logged to /workspace/pipeline.log. On failure the script stops
# with an unmistakable "PIPELINE FAILED" block — it never continues silently.
#
# External-network note: the only external fetches here are pip (PyPI) and the
# HF Hub download inside python. pip gets an SSL fallback (--trusted-host) that
# activates ONLY on certificate errors. No git/curl to external hosts is used;
# if you add one, follow the same rule: try normally first, relax cert checks
# only when the failure is specifically a certificate error.
# =============================================================================
set -u -o pipefail

LOG=/workspace/pipeline.log
exec > >(tee -a "$LOG") 2>&1

REPO=/workspace/flowforge
VENV=/root/.unsloth/studio/unsloth_studio
export MODEL_ID="unsloth/gemma-4-E4B-it"          # MUST stay Gemma (prize eligibility)
export FLOWFORGE_BASE_MODEL="$MODEL_ID"           # ml/model_setup.py reads this
export MERGED_DIR="$REPO/ml/outputs/merged-gemma-flowforge"
export BASE_EVAL_JSON=/workspace/eval_base.json
export FT_EVAL_JSON=/workspace/eval_ft.json
EVAL_LIMIT=100
export PYTHONUNBUFFERED=1
export HF_HUB_DISABLE_XET=1
# gfx1100 is natively supported by ROCm — deliberately NOT setting HSA_OVERRIDE_GFX_VERSION.

die() {
  echo ""
  echo "################################################################"
  echo "##  PIPELINE FAILED"
  echo "##  Reason: $1"
  echo "##  Stopped at: $(date -u +%FT%TZ)"
  echo "##  Full log:  $LOG  (bring this file back for the next fix)"
  echo "################################################################"
  exit 1
}

step() { echo ""; echo "==== STEP $1: $2 ===="; echo "[time] $(date -u +%FT%TZ)"; }

# pip wrapper: ALWAYS python3 -m pip (bare pip may hit system python on this
# pod). SSL fallback fires only on certificate errors, never on other failures.
pip_install() {
  local out rc
  out=$(python3 -m pip install "$@" 2>&1); rc=$?
  echo "$out"
  if [ $rc -ne 0 ] && echo "$out" | grep -qiE "certificate verify|SSLError|SSL: CERTIFICATE"; then
    echo "[ssl-fallback] certificate error from pip — retrying with --trusted-host"
    python3 -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org "$@"
    rc=$?
  fi
  return $rc
}

echo ""
echo "======================================================================"
echo " FlowForge pipeline starting  $(date -u +%FT%TZ)"
echo "======================================================================"

# ---------------------------------------------------------------------------
step 0 "repo hygiene (/workspace/flowforge, git origin, no .env)"
# ---------------------------------------------------------------------------
cd "$REPO" 2>/dev/null || die "repo not found at $REPO — clone it there first"
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "$REPO is not a git repository"
ORIGIN=$(git remote get-url origin 2>/dev/null || echo "NONE")
echo "[hygiene] git origin: $ORIGIN"
case "$ORIGIN" in
  *github.com*rufatj/flowforge*) echo "[hygiene] origin OK" ;;
  *) die "unexpected git origin '$ORIGIN' (want github.com/rufatj/flowforge) — wrong clone?" ;;
esac
if [ -f "$REPO/.env" ]; then
  echo "[hygiene][WARNING] .env exists in $REPO — it is gitignored and should never"
  echo "[hygiene][WARNING] have reached this pod. NOT deleting it automatically;"
  echo "[hygiene][WARNING] inspect it yourself (it may contain API keys)."
else
  echo "[hygiene] no .env present — good"
fi
[ -f "$REPO/data/out/heldout.jsonl" ] || die "data/out/heldout.jsonl missing — data/out/* is gitignored, upload heldout.jsonl (and train.jsonl for training) to the pod first"
[ -f "$REPO/data/out/train.jsonl" ]   || die "data/out/train.jsonl missing — upload it to the pod first (gitignored, not in the clone)"

# ---------------------------------------------------------------------------
step 1 "activate venv, verify python/pip, verify GPU visible to torch"
# ---------------------------------------------------------------------------
[ -f "$VENV/bin/activate" ] || die "venv not found at $VENV"
# shellcheck disable=SC1091
source "$VENV/bin/activate"
echo "[venv] python3 -> $(command -v python3)"
echo "[venv] pip module -> $(python3 -m pip --version 2>&1)"
python3 - <<'PY' || die "python is not the unsloth_studio venv python"
import sys
assert sys.prefix.startswith("/root/.unsloth/studio/unsloth_studio"), f"wrong python: {sys.executable}"
print(f"[venv] confirmed venv python {sys.version.split()[0]} at {sys.executable}")
PY
python3 - <<'PY' || die "torch.cuda.is_available() is False — GPU not visible (quota reset? wrong image?). Do not proceed."
import torch
assert torch.cuda.is_available(), "torch.cuda.is_available() returned False"
name = torch.cuda.get_device_name(0)
vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
print(f"[gpu] {name} — {vram:.1f} GB VRAM — torch {torch.__version__}")
PY

# ---------------------------------------------------------------------------
step 2 "pin transformers==5.5.0, then PROVE the Gemma-4 tokenizer loads"
# ---------------------------------------------------------------------------
T0=$(date +%s)
pip_install "transformers==5.5.0" || die "pip install transformers==5.5.0 failed (see output above)"
python3 - <<'PY'
import os, sys, traceback
mid = os.environ["MODEL_ID"]
try:
    import transformers
    print(f"[check] transformers version after pin: {transformers.__version__}")
    if transformers.__version__ != "5.5.0":
        print(f"[check] EXPECTED 5.5.0 — pip resolved something else"); sys.exit(44)
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(mid)
    ids = tok.apply_chat_template([{"role": "user", "content": "ping"}],
                                  tokenize=True, add_generation_prompt=True)
    assert len(ids) > 0
    print(f"[check] tokenizer OK — {len(ids)} tokens for smoke prompt")
except SystemExit:
    raise
except Exception:
    tb = traceback.format_exc()
    print(tb)
    if "has no attribute 'keys'" in tb:
        print("################################################################")
        print("##  TOKENIZER STILL BROKEN AT 5.5.0")
        print("##  The 'list object has no attribute keys' bug is NOT fixed by")
        print("##  transformers 5.5.0. Full traceback is above — bring it back")
        print("##  for the next fix. NOT proceeding blindly.")
        print("################################################################")
        sys.exit(42)
    sys.exit(43)
PY
rc=$?
case $rc in
  0)  echo "[check] tokenizer gate passed — proceeding" ;;
  42) die "TOKENIZER STILL BROKEN AT 5.5.0 (traceback above)" ;;
  44) die "transformers version after install is not 5.5.0 — pin did not take effect" ;;
  *)  die "tokenizer failed with a DIFFERENT error than the known bug (traceback above)" ;;
esac

# ---------------------------------------------------------------------------
step 3 "baseline eval — gates 1+2 only, local transformers inference"
# ---------------------------------------------------------------------------
cat > /workspace/local_eval.py <<'PY'
"""Local-inference eval: gates 1 (JSON) + 2 (schema) only. No HTTP, no n8n.
Reads system+user prompts straight from heldout.jsonl so they exactly match
training. Reuses eval.harness.run_gates(live_import=False)."""
import argparse, json, sys
sys.path.insert(0, "/workspace/flowforge")
from eval.harness import run_gates  # needs only requests+stdlib, not openai


def load_rows(limit):
    rows = []
    with open("/workspace/flowforge/data/out/heldout.jsonl", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                m = json.loads(line)["messages"]
                rows.append((next(x["content"] for x in m if x["role"] == "system"),
                             next(x["content"] for x in m if x["role"] == "user")))
            if limit and len(rows) >= limit:
                break
    return rows


def load_model(path):
    import torch, transformers
    last = None
    for cls_name in ("AutoModelForCausalLM", "AutoModelForImageTextToText"):
        try:
            cls = getattr(transformers, cls_name)
            m = cls.from_pretrained(path, torch_dtype=torch.bfloat16, device_map="auto")
            print(f"[eval] loaded {path} via {cls_name}", flush=True)
            return m
        except Exception as e:
            print(f"[eval] {cls_name} failed: {str(e)[:200]}", flush=True)
            last = e
    raise last


def build_inputs(tok, system, user):
    try:
        return tok.apply_chat_template(
            [{"role": "system", "content": system}, {"role": "user", "content": user}],
            tokenize=True, add_generation_prompt=True, return_tensors="pt")
    except Exception:  # some Gemma templates reject a system role — fold it in
        return tok.apply_chat_template(
            [{"role": "user", "content": system + "\n\n" + user}],
            tokenize=True, add_generation_prompt=True, return_tensors="pt")


def main():
    import torch
    from transformers import AutoTokenizer
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--limit", type=int, default=100)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    tok = AutoTokenizer.from_pretrained(a.model)
    model = load_model(a.model)
    model.eval()
    rows = load_rows(a.limit)
    print(f"[eval] {a.label}: {len(rows)} heldout prompts", flush=True)

    g1 = g2 = 0
    for i, (system, user) in enumerate(rows, 1):
        inputs = build_inputs(tok, system, user).to(model.device)
        with torch.no_grad():
            out = model.generate(input_ids=inputs, max_new_tokens=4096, do_sample=False)
        text = tok.decode(out[0][inputs.shape[1]:], skip_special_tokens=True)
        r = run_gates(text, live_import=False)
        g1 += r.json_valid
        g2 += r.schema_valid
        print(f"  [{i}/{len(rows)}] json={r.json_valid} schema={r.schema_valid}", flush=True)

    n = len(rows)
    res = {"label": a.label, "model": a.model, "total": n,
           "gate1": round(g1 / n, 4), "gate2": round(g2 / n, 4),
           "gate3": None}  # live import impossible from this pod
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
    print(f"[eval] {a.label}: gate1={res['gate1']:.1%} gate2={res['gate2']:.1%} -> {a.out}", flush=True)


main()
PY
python3 /workspace/local_eval.py --model "$MODEL_ID" --label base-gemma-4-E4B \
  --limit "$EVAL_LIMIT" --out "$BASE_EVAL_JSON" \
  || die "baseline eval failed (see traceback above)"

# ---------------------------------------------------------------------------
step 4 "SFT training with checkpointing + automatic OOM fallbacks"
# ---------------------------------------------------------------------------
# Idempotent patches: (a) checkpoint every 50 steps (survives quota resets —
# repo lives under /workspace so ml/outputs/checkpoints is on /workspace),
# (b) auto-resume from the latest checkpoint if one exists.
python3 - <<'PY' || die "failed to patch checkpointing/resume"
import pathlib, re
tc = pathlib.Path("/workspace/flowforge/ml/train_config.py")
src = tc.read_text(encoding="utf-8")
if "save_steps" not in src:
    src = src.replace('save_strategy="epoch",',
                      'save_strategy="steps", save_steps=50, save_total_limit=2,')
    tc.write_text(src, encoding="utf-8")
    print("[patch] train_config.py: checkpoint every 50 steps, keep last 2")
else:
    print("[patch] train_config.py: checkpointing already patched")

ft = pathlib.Path("/workspace/flowforge/ml/finetune_sft.py")
src = ft.read_text(encoding="utf-8")
if "resume_from_checkpoint" not in src:
    old = "    trainer.train()"
    new = ('    import glob as _glob\n'
           '    _ckpts = _glob.glob(str(ADAPTER_DIR.parent / "checkpoints" / "checkpoint-*"))\n'
           '    print(f"[resume] found {len(_ckpts)} checkpoint(s)" )\n'
           '    trainer.train(resume_from_checkpoint=True if _ckpts else None)')
    assert old in src, "expected 'trainer.train()' line not found in finetune_sft.py"
    ft.write_text(src.replace(old, new), encoding="utf-8")
    print("[patch] finetune_sft.py: auto-resume from latest checkpoint")
else:
    print("[patch] finetune_sft.py: resume already patched")
PY

apply_oom_row1() {  # docs/gpu-oom-fallbacks.md row: batch 2->1, grad-accum 8->16
  python3 - <<'PY'
import pathlib, re
p = pathlib.Path("/workspace/flowforge/ml/train_config.py")
src = p.read_text(encoding="utf-8")
src = re.sub(r"PER_DEVICE_BATCH = \d+", "PER_DEVICE_BATCH = 1", src)
src = re.sub(r"GRAD_ACCUM = \d+", "GRAD_ACCUM = 16", src)
p.write_text(src, encoding="utf-8")
print("[oom-fallback 1] PER_DEVICE_BATCH=1, GRAD_ACCUM=16 (effective batch unchanged)")
PY
}

apply_oom_row2() {  # docs/gpu-oom-fallbacks.md row: seq-len 8192->4096
  python3 - <<'PY'
import pathlib, re
p = pathlib.Path("/workspace/flowforge/ml/model_setup.py")
src = p.read_text(encoding="utf-8")
src = re.sub(r"MAX_SEQ_LENGTH = \d+", "MAX_SEQ_LENGTH = 4096", src)
p.write_text(src, encoding="utf-8")
print("[oom-fallback 2] MAX_SEQ_LENGTH=4096 (avg example ~2.5k tokens; few truncate)")
PY
}

train_once() {  # $1 = attempt log file
  ( cd "$REPO" && python3 -m ml.finetune_sft ) 2>&1 | tee "$1"
  return "${PIPESTATUS[0]}"
}

is_oom() {
  grep -qiE "out of memory|OutOfMemoryError|hipErrorOutOfMemory|HIP out of memory|CUDA out of memory" "$1"
}

echo "[train] attempt 1/3 — batch 2, grad-accum 8, seq 8192"
if ! train_once /workspace/train_attempt1.log; then
  if is_oom /workspace/train_attempt1.log; then
    echo "[train] attempt 1 hit OOM — applying fallback row 1 and retrying"
    apply_oom_row1
    echo "[train] attempt 2/3 — batch 1, grad-accum 16, seq 8192"
    if ! train_once /workspace/train_attempt2.log; then
      if is_oom /workspace/train_attempt2.log; then
        echo "[train] attempt 2 hit OOM — applying fallback row 2 and retrying"
        apply_oom_row2
        echo "[train] attempt 3/3 — batch 1, grad-accum 16, seq 4096"
        if ! train_once /workspace/train_attempt3.log; then
          if is_oom /workspace/train_attempt3.log; then
            die "training STILL OOMs after both documented fallbacks (batch 1 + seq 4096). Not looping further — see docs/gpu-oom-fallbacks.md rows 4+ for the manual paths."
          else
            die "training attempt 3 failed with a NON-OOM error (see /workspace/train_attempt3.log)"
          fi
        fi
      else
        die "training attempt 2 failed with a NON-OOM error (see /workspace/train_attempt2.log)"
      fi
    fi
  else
    die "training failed with a NON-OOM error — no point retrying with smaller batches (see /workspace/train_attempt1.log)"
  fi
fi
echo "[train] training finished successfully"

[ -d "$MERGED_DIR" ] && [ -n "$(ls -A "$MERGED_DIR" 2>/dev/null)" ] \
  || die "training reported success but merged model is missing/empty at $MERGED_DIR"
echo "[train] merged model present at $MERGED_DIR"

# ---------------------------------------------------------------------------
step 5 "fine-tuned eval — same gates 1+2, merged model"
# ---------------------------------------------------------------------------
python3 /workspace/local_eval.py --model "$MERGED_DIR" --label fine-tuned-gemma-4-E4B \
  --limit "$EVAL_LIMIT" --out "$FT_EVAL_JSON" \
  || die "fine-tuned eval failed (see traceback above)"

# ---------------------------------------------------------------------------
step 6 "summary"
# ---------------------------------------------------------------------------
T1=$(date +%s)
export WALL_SECONDS=$((T1 - T0))
python3 - <<'PY'
import json, os
b = json.load(open(os.environ["BASE_EVAL_JSON"]))
f = json.load(open(os.environ["FT_EVAL_JSON"]))
w = int(os.environ["WALL_SECONDS"])
print()
print("=================== FINAL SUMMARY ===================")
print(f"{'Gate':<22}{'base':>10}{'fine-tuned':>14}{'delta':>10}")
print("-" * 56)
for g, lbl in (("gate1", "JSON valid"), ("gate2", "schema valid")):
    print(f"{g} ({lbl})".ljust(22) + f"{b[g]:>9.1%}{f[g]:>13.1%}{f[g]-b[g]:>+10.1%}")
print("-" * 56)
print(f"n = {b['total']} heldout prompts per side (gates 1+2 only; gate 3 runs")
print("on the local machine against live n8n — this pod cannot reach it)")
print(f"wall clock (steps 2-5): {w//3600}h {w%3600//60}m {w%60}s")
print(f"merged model for serving: {os.environ['MERGED_DIR']}")
print(f"eval JSONs: {os.environ['BASE_EVAL_JSON']}  {os.environ['FT_EVAL_JSON']}")
print("======================================================")
PY

echo ""
echo "PIPELINE COMPLETE  $(date -u +%FT%TZ)  — full log at $LOG"
