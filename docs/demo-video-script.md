# FlowForge — 3-minute demo video script

Read the **VOICE** lines almost verbatim. **SCREEN** tells you what to show while saying it.
Fill the `___%` numbers from `eval/results/comparison.json` before recording.
Target: 3:00 total. Rehearse once with a timer — every section has a hard out.

---

## 0:00–0:25 — The problem (25s)

**SCREEN:** n8n's editor open on a blank canvas. Briefly hover the paid AI assistant / pricing page tab.

**VOICE:**
> "This is n8n — one of the most popular open-source automation tools in the world. It has an AI copilot that builds workflows from plain English… but it's paid, closed, and cloud-only. Every prompt you type — your business logic, your data schemas — leaves your infrastructure. For a tool whose whole promise is *self-hosting*, that's backwards. So I built FlowForge: an open-source, self-hosted alternative, powered by a Gemma model fine-tuned on an AMD Radeon PRO W7900."

---

## 0:25–1:10 — Live generation (45s)

**SCREEN:** FlowForge Generate page. Type the request live (have it in clipboard as backup):
*"When a customer sends a message on Instagram, classify their intent, and if they want to buy something, add them to Google Sheets and notify me on Telegram."* Click Generate. While it streams, point at the JSON.

**VOICE:**
> "I'll describe an automation the way a real user would — no node names, no technical terms. [type/paste, click Generate] FlowForge returns actual n8n workflow JSON — real node types, correct type versions, and the notoriously tricky double-nested connections wiring that generic LLMs almost always get wrong. This isn't a mock-up — this came from Gemma, fine-tuned with LoRA on about five and a half thousand real workflow examples, running on hardware I control."

---

## 1:10–1:50 — Import into live n8n + test (40s)

**SCREEN:** Click the Import button on the Result page → switch to the n8n tab → the workflow is there; open it, show the nodes wired up. If it's webhook-triggered, show the auto-generated test form and fire it once.

**VOICE:**
> "Now the moment of truth: one click sends it through n8n's REST API into a live instance. [switch tabs] And there it is — every node placed, every connection wired. FlowForge even generates a test form for webhook-triggered workflows so you can fire them immediately. No copy-pasting JSON, no fixing broken imports by hand."

---

## 1:50–2:35 — The proof: before vs after (45s)

**SCREEN:** The Proof page with the before/after chart (or the printed `compare_before_after` table). Point at each gate as you mention it.

**VOICE:**
> "But does fine-tuning actually matter? I benchmarked it with a three-gate harness on 810 held-out prompts the model never saw in training. Gate one: is the output valid JSON? Gate two: is it a structurally correct n8n workflow? And gate three — the one that matters — does a *live n8n instance* actually accept the import? Base Gemma, before fine-tuning: ___% valid JSON, ___% valid schema, and just ___% survive a real import. After LoRA fine-tuning on the AMD W7900: ___%, ___%, and ___% importable. [pause half a second] And to be sure the benchmark itself is honest, the training data was validated through the same gates first — the ground truth imports at effectively one hundred percent."

---

## 2:35–3:00 — Close (25s)

**SCREEN:** README on GitHub — scroll slowly past the architecture diagram and Results table. End on the repo URL, full screen.

**VOICE:**
> "Everything is open: MIT-licensed code, open training data from public community templates, open Gemma weights, and the full data-to-benchmark pipeline — collected, cleaned, enriched, trained, and proven on AMD hardware. Your automations, your prompts, your infrastructure. FlowForge — describe it, import it, run it. The repo link is on screen."

---

## Recording checklist

- [ ] Fill all `___%` from `eval/results/comparison.json`
- [ ] n8n test instance running and logged in (clean workflow list — delete leftovers)
- [ ] Backend `MODEL_MODE=amd` pointed at the pod endpoint; do one warm-up generation off-camera (first LangChain-node import can be slow on a cold n8n)
- [ ] Demo prompt in clipboard; browser zoom ~125% so JSON is readable on video
- [ ] Close every unrelated tab/notification; hide bookmarks bar
- [ ] Timer visible while rehearsing — hard outs at 0:25 / 1:10 / 1:50 / 2:35
