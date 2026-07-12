# FlowForge — 3-minute demo video script

Read the **VOICE** lines almost verbatim. **SCREEN** tells you what to show while saying it.
All numbers here are **final and measured** — nothing to fill in.
Target: 3:00 total. Rehearse once with a timer — every section has a hard out.

> **Before recording:** the model succeeds on ~20% of prompts, and the demo must show a
> *working* one. Off-camera, run 3–4 candidate prompts through Generate and pick one that
> produces a clean, mid-size workflow that imports. Lock that exact prompt + its output in.
> Demoing a known-good case is fair — the Proof section is where you're honest about the 20%.

---

## 0:00–0:25 — The problem (25s)

**SCREEN:** n8n's editor open on a blank canvas. Briefly hover the paid AI assistant / pricing page tab.

**VOICE:**
> "This is n8n — one of the most popular open-source automation tools in the world. It has an AI copilot that builds workflows from plain English… but it's paid, closed, and cloud-only. Every prompt you type — your business logic, your data schemas — leaves your infrastructure. For a tool whose whole promise is *self-hosting*, that's backwards. So I built FlowForge: an open-source, self-hosted alternative, powered by Gemma-3-4B fine-tuned on a single AMD Radeon PRO W7900."

---

## 0:25–1:10 — Live generation (45s)

**SCREEN:** FlowForge Generate page. Paste the pre-tested prompt (in clipboard). Click Generate. While it streams, point at the JSON — the node types, the connections block.

**VOICE:**
> "I'll describe an automation the way a real user would — no node names, no technical terms. [paste, click Generate] FlowForge returns actual n8n workflow JSON — real node types, correct type versions, and the notoriously tricky double-nested connections wiring that generic LLMs get wrong. This came from Gemma-3-4B, fine-tuned with LoRA on thousands of real community workflows, running entirely on AMD hardware I control — no cloud, no API calls leaving the box."

---

## 1:10–1:50 — Import into live n8n + test (40s)

**SCREEN:** Click Import on the Result page → switch to the n8n tab → the workflow is there; open it, show the nodes wired up. If it's webhook-triggered, show the auto-generated test form and fire it once.

**VOICE:**
> "Now the moment of truth: one click sends it through n8n's REST API into a live instance. [switch tabs] And there it is — every node placed, every connection wired, ready to run. FlowForge even generates a test form for webhook-triggered workflows so you can fire them immediately. No copy-pasting JSON, no hand-fixing broken imports."

---

## 1:50–2:35 — The proof: 0% → 20% (45s)

**SCREEN:** The Proof page / a simple two-bar chart: base 0%, fine-tuned 20%. Point at each bar.

**VOICE:**
> "But does the fine-tuning actually matter? I benchmarked it honestly — same prompts, same generation settings, before and after. Stock Gemma-3-4B, out of the box, scores **zero percent**: it produces not a single valid n8n workflow. It simply doesn't know the schema. After LoRA fine-tuning on the W7900, that jumps to **twenty percent** of held-out prompts generating a fully valid, structurally-correct workflow. And here's the detail I like most: every single time the fine-tuned model emits parseable JSON, that JSON is *always* a valid n8n workflow — it learned the structure completely. The only thing standing between us and a much higher number is the very longest workflows getting cut off mid-generation — a length limit, not a correctness problem. That's a knob, and I know exactly where it is."

---

## 2:35–3:00 — Close (25s)

**SCREEN:** README on GitHub — scroll slowly past the architecture diagram, the Results table, and the "Lessons Learned" section. End on the repo URL, full screen.

**VOICE:**
> "Everything is open: MIT-licensed code, open community training data, open Gemma-3 weights, and the full pipeline — collected, cleaned, trained, and benchmarked on AMD. I even documented the two traps that cost me GPU hours, so the next person doesn't hit them. Your automations, your prompts, your infrastructure. FlowForge — describe it, import it, run it. The repo link is on screen."

---

## Recording checklist

- [ ] **Pre-test and lock a known-good prompt** (~20% hit rate — never generate blind on camera)
- [ ] n8n test instance running and logged in (clean workflow list — delete leftovers)
- [ ] Backend `MODEL_MODE=amd` pointed at the pod endpoint; do one warm-up generation off-camera (first import can be slow on a cold n8n)
- [ ] Browser zoom ~125% so the JSON is readable on video
- [ ] Close every unrelated tab/notification; hide bookmarks bar
- [ ] Timer visible while rehearsing — hard outs at 0:25 / 1:10 / 1:50 / 2:35
- [ ] Numbers to say out loud: **0% → 20%**, "Gemma-3-4B", "AMD Radeon PRO W7900"
