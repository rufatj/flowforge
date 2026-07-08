import Reveal from "../Reveal.jsx";
import Eyebrow from "./Eyebrow.jsx";

const STEPS = [
  { k: "01", t: "You write a sentence", d: "Plain language, the way you would ask a teammate. No schema, no syntax." },
  { k: "02", t: "The model composes", d: "A Gemma model fine tuned on real automations drafts the nodes and their wiring." },
  { k: "03", t: "Three gates verify", d: "The output must parse, match the n8n schema, and pass a live import. Nothing ships unchecked." },
  { k: "04", t: "It lands in your n8n", d: "One click and the workflow is live in your own instance, ready to run." },
  { k: "05", t: "You refine and own it", d: "Open weights and open evaluation mean you can see why it works and make it sharper." },
];

// The path from idea to running automation, as a vertical timeline. The spine
// draws down on reveal; each stop fades in with a small stagger.
export default function Timeline() {
  return (
    <section id="journey" className="scroll-mt-24 py-28">
      <div className="mx-auto max-w-3xl px-6">
        <Eyebrow label="The path" title="From idea to a running automation" align="center" />

        <div className="relative mt-16 pl-10">
          <Reveal className="absolute left-[14px] top-1 h-full w-px origin-top bg-gradient-to-b from-accent/70 via-accent/25 to-transparent"
            style={{ animation: "draw-line 1.1s cubic-bezier(0.22,1,0.36,1) both" }} />
          <ol className="space-y-11">
            {STEPS.map((s, i) => (
              <Reveal as="li" key={s.k} delay={i * 90} className="relative">
                <span className="absolute -left-10 top-0 flex h-7 w-7 items-center justify-center rounded-full border border-accent/40 bg-ink-950 font-mono text-[11px] text-accent shadow-[0_0_16px_-4px_rgba(56,189,248,0.7)]">
                  {s.k}
                </span>
                <h3 className="text-lg font-semibold text-zinc-100">{s.t}</h3>
                <p className="mt-2 text-[15px] leading-relaxed text-zinc-400">{s.d}</p>
              </Reveal>
            ))}
          </ol>
        </div>
      </div>
    </section>
  );
}
