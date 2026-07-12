# FlowForge — 5-slide hackathon deck (content outline)

Content only; design later. All numbers below are **final and measured**.
Rule of thumb: each slide supports ~35 seconds of talking.

---

## Slide 1 — Title & one-liner

- **FlowForge** — *Describe your automation in plain language. Get a working, importable n8n workflow.*
- Open-source, self-hosted alternative to n8n's paid AI copilot
- **Gemma-3-4B + LoRA**, fine-tuned on **AMD Radeon PRO W7900 (gfx1100, RDNA3, 48 GB, ROCm)**
- Name / solo builder / AMD Hackathon ACT II, Track 3
- (visual: one screenshot of the Generate page with a finished workflow JSON)

## Slide 2 — Problem & why now

- n8n's built-in AI assistant: **paid, closed, cloud-only** — prompts, business logic, and data schemas leave your infrastructure
- Contradiction: people choose n8n *to self-host*, then bolt on a cloud AI dependency
- Generic LLMs fail at n8n JSON: hallucinated node types, wrong `typeVersion`s, broken double-nested `connections` wiring — imports fail
- Proof of how hard it is: **stock Gemma-3-4B scores 0%** on this task (see slide 4)
- The gap: nobody ships an **open model + open data + import-verified** pipeline you can run yourself

## Slide 3 — What I built (architecture)

- Pipeline: **2,711 real community templates → cleaned to 1,800 → 5,400 chat pairs** (3× LLM-rewritten natural requests) → 85/15 split by template id, no leakage → 4,590 train / 810 heldout
- **LoRA SFT** (r=16, α=32, on q/k/v/o/gate/up/down_proj) via plain `transformers.Trainer` + PEFT on a single W7900 — **1 epoch, 269 steps, loss 1.43 → 0.90, 3 h 35 m**
- vLLM (OpenAI-compatible) → FastAPI backend → React frontend → **one-click import into live n8n** + auto-generated webhook test forms
- Everything swappable via env: dev endpoint ↔ self-hosted AMD endpoint
- (visual: the architecture diagram from the README)

## Slide 4 — Proof: before vs after (the money slide)

- Same harness, same generation settings (greedy, `repetition_penalty=1.1`, `no_repeat_ngram_size=6`, `max_new_tokens=6144`), 30 held-out prompts never seen in training
- Gate 1 = valid JSON · Gate 2 = valid n8n schema (nodes + connections + every node has name & type)

| | Gate 1 · JSON | Gate 2 · Schema |
|---|---|---|
| Base `gemma-3-4b-it` | **0.0%** | **0.0%** |
| **FlowForge LoRA** | **20.0%** | **20.0%** |

- **The headline: 0% → 20%.** Fine-tuning makes an impossible task possible — base Gemma produces *zero* valid workflows.
- **Gate 1 == Gate 2:** whenever the model emits parseable JSON, it's *always* a schema-valid n8n workflow. It learned the structure; the only failures left are the longest workflows getting cut off mid-JSON (a generation-length limit, not a correctness problem).
- Honesty note: live-import gate (Gate 3) validated separately on ground-truth data (100% import of schema-valid); the pod couldn't reach n8n, so the model before/after covers Gates 1–2.
- (visual: two-bar before/after chart, 0% vs 20%)

## Slide 5 — Why it matters & what's next

- **Open everything:** MIT code, public community training data, open Gemma-3 weights, reproducible pipeline (`collect → clean → enrich → split → train → eval`)
- **AMD story:** full fine-tune + inference on a single Radeon PRO W7900 (RDNA3 workstation card) — no CUDA, no cloud AI dependency
- **Two findings we're contributing back** (undocumented elsewhere): Gemma-4 can't LoRA-train on PEFT/Unsloth on RDNA3 yet; and the sequence-length trap — truncating long JSON at `max_len` teaches the model workflows never end (0% → fixed by `max_len=6144`)
- Next: raise 20% via longer generation budget + 2nd epoch; GRPO with the import-gate as reward; broader node coverage
- Call to action: repo URL + "clone it, point it at your n8n, own your copilot"
