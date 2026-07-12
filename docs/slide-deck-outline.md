# FlowForge — 5-slide hackathon deck (content outline)

Content only; design later. Fill `___%` from `eval/results/comparison.json`.
Rule of thumb: each slide supports ~35 seconds of talking.

---

## Slide 1 — Title & one-liner

- **FlowForge** — *Describe your automation in plain language. Get a working, importable n8n workflow.*
- Open-source, self-hosted alternative to n8n's paid AI copilot
- Gemma + LoRA, fine-tuned and served on **AMD Radeon PRO W7900 (ROCm)**
- Name / solo builder / AMD Hackathon ACT II, Track 3
- (visual: one screenshot of the Generate page with a finished workflow JSON)

## Slide 2 — Problem & why now

- n8n's built-in AI assistant: **paid, closed, cloud-only** — prompts, business logic, and data schemas leave your infrastructure
- Contradiction: people choose n8n *to self-host*, then bolt on a cloud AI dependency
- Generic LLMs fail at n8n JSON: hallucinated node types, wrong `typeVersion`s, broken double-nested `connections` wiring — imports fail
- The gap: nobody ships an **open model + open data + live-import-verified** pipeline you can run yourself

## Slide 3 — What I built (architecture)

- Pipeline: **1,800 real community workflows → cleaned → 5,400 chat pairs** (LLM-rewritten natural requests) → 85/15 split by template id (no leakage)
- **16-bit LoRA SFT** (r=16, α=32, attn+MLP) with Unsloth on ROCm — single W7900, 48 GB
- Served with **vLLM** (OpenAI-compatible) → FastAPI backend → React frontend → **one-click import into live n8n** + auto-generated webhook test forms
- Everything swappable via env: dev endpoint ↔ self-hosted AMD endpoint
- (visual: the architecture diagram from the README)

## Slide 4 — Proof: three-gate benchmark (the money slide)

- Three gates, each strictly harder: **① valid JSON → ② valid n8n schema → ③ a LIVE n8n instance accepts the import** (REST API, node count verified)
- 810 held-out prompts, never seen in training

| | JSON | Schema | **Live import** |
|---|---|---|---|
| Base Gemma | \_\_\_% | \_\_\_% | \_\_\_% |
| **FlowForge SFT** | \_\_\_% | \_\_\_% | **\_\_\_%** |

- Benchmark honesty: ground-truth training targets score ~100% through the same gates — the harness measures the model, not dataset noise
- (visual: before/after bar chart from the Proof page)

## Slide 5 — Why it matters & what's next

- **Open everything:** MIT code, public community training data, open Gemma weights, reproducible pipeline (`collect → clean → enrich → split → train → eval`, each one command)
- **AMD story:** full fine-tune + inference on a single Radeon PRO W7900 — no CUDA, no cloud AI dependency
- Next: GRPO with the import-gate as reward signal, broader node coverage, community dataset v2
- Call to action: repo URL + "clone it, point it at your n8n, own your copilot"
