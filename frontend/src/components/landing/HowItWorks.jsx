import Reveal from "../Reveal.jsx";
import Eyebrow from "./Eyebrow.jsx";
import { useTilt } from "../../hooks/useTilt.js";
import { Describe, Import } from "./icons.jsx";

const CARDS = [
  { key: "describe", title: "Describe", icon: <Describe className="h-6 w-6" />,
    body: "Write what you want in plain language. No canvas, no drag and drop, no learning curve." },
  { key: "generate", title: "Generate", gif: "/assets/circle.gif",
    body: "A Gemma model, fine tuned on thousands of real workflows, returns valid workflow JSON in seconds." },
  { key: "import", title: "Import", icon: <Import className="h-6 w-6" />,
    body: "One click sends it into your n8n instance. Webhook inputs receive a test form on their own. Everything stays local." },
];

function Visual({ card }) {
  if (card.gif) {
    return (
      <div className="flex h-14 w-14 items-center justify-center overflow-hidden rounded-xl border border-white/10 bg-ink-950">
        <img src={card.gif} alt="A model composing a workflow" className="h-full w-full object-cover" />
      </div>
    );
  }
  return (
    <div className="flex h-14 w-14 items-center justify-center rounded-xl border border-white/10 bg-white/[0.03] text-accent">
      {card.icon}
    </div>
  );
}

// Each card reveals in sequence (long stagger reads as one-by-one), then
// carries physical weight under the cursor via a gentle 3D tilt.
function Card({ card, index }) {
  const tiltRef = useTilt({ max: 6, scale: 1.015 });
  return (
    <Reveal delay={index * 220}>
      <div ref={tiltRef}
        className="tilt group h-full rounded-2xl border border-white/[0.07] bg-white/[0.02] p-8 hover:border-accent/25 hover:bg-white/[0.035] hover:shadow-[0_0_40px_-12px_rgba(56,189,248,0.35)]">
        <Visual card={card} />
        <h3 className="mt-6 text-lg font-semibold text-zinc-100">{card.title}</h3>
        <p className="mt-3 text-[15px] leading-relaxed text-zinc-400">{card.body}</p>
      </div>
    </Reveal>
  );
}

export default function HowItWorks() {
  return (
    <section id="how" className="scroll-mt-24 py-28">
      <div className="mx-auto max-w-6xl px-6">
        <Eyebrow label="The flow" title="From a sentence to a workflow that runs" />
        <div className="mt-16 grid gap-6 md:grid-cols-3">
          {CARDS.map((card, i) => <Card key={card.key} card={card} index={i} />)}
        </div>
      </div>
    </section>
  );
}
