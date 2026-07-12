import { useState } from "react";
import Reveal from "../Reveal.jsx";
import Eyebrow from "./Eyebrow.jsx";
import { useReveal } from "../../hooks/useReveal.js";
import { useScrollSpin } from "../../hooks/useScrollSpin.js";

const TAGS = [
  "Webhook", "HTTP Request", "IF", "Switch", "Loop Over Items", "Google Sheets",
  "Telegram", "Slack", "Gmail", "AI Agent", "LangChain Tools", "Memory Buffer",
];

// Five voices for the same sentence; each click on the paragraph re-dresses it.
const FONTS = [
  "'Inter', sans-serif",
  "'JetBrains Mono', monospace",
  "'Playfair Display', serif",
  "'Space Grotesk', sans-serif",
  "'Caveat', cursive",
];

export default function Knows() {
  const spinRef = useScrollSpin({ turns: 0.55 });
  const [fontIndex, setFontIndex] = useState(0);
  const tagsReveal = useReveal({ threshold: 0.3 });

  return (
    <section id="knows" className="scroll-mt-24 overflow-hidden py-28">
      <div className="mx-auto max-w-6xl px-6">
        <Eyebrow label="Depth" title="Built on real workflows" align="center" />
      </div>

      {/* Full-bleed orb: spins with the scroll, settles exactly at center. */}
      <div className="mt-4 w-screen ml-[calc(50%-50vw)] mr-[calc(50%-50vw)] overflow-hidden">
        <img
          ref={spinRef}
          src="/assets/integration-ways.png"
          alt="A central engine wired to Gmail, Google Drive, Slack, Teams, Zoom and WhatsApp"
          className="h-[46vh] min-h-[320px] w-full select-none object-cover will-change-transform sm:h-[62vh]"
          style={{ WebkitMaskImage: "linear-gradient(to bottom, transparent, #000 22%, #000 78%, transparent)",
            maskImage: "linear-gradient(to bottom, transparent, #000 22%, #000 78%, transparent)" }}
        />
      </div>

      <div className="mx-auto -mt-6 max-w-3xl px-6">
        <Reveal>
          <p
            onClick={() => setFontIndex((i) => (i + 1) % FONTS.length)}
            title="Click to change the voice"
            className="cursor-pointer text-center text-[15px] leading-relaxed text-zinc-400 transition-colors duration-300 hover:text-zinc-200"
            style={{ fontFamily: FONTS[fontIndex] }}
          >
            The model learned from thousands of community workflows spanning webhooks, HTTP requests,
            conditional and switch logic, loops over items, Google Sheets, Telegram, Slack, Gmail, and
            the modern AI Agent node with its tools and memory. It understands the exact JSON shape n8n
            expects.
          </p>
        </Reveal>

        {/* Node tags arrive one by one, like a stream of notifications. */}
        <div ref={tagsReveal.ref} className="mt-9 flex flex-wrap justify-center gap-2">
          {TAGS.map((tag, i) => (
            <span
              key={tag}
              className={`rounded-full border border-white/10 bg-white/[0.03] px-3 py-1 font-mono text-[13px] text-zinc-400 transition-colors duration-200 hover:border-accent/30 hover:text-zinc-200 ${tagsReveal.visible ? "animate-tag-pop" : "opacity-0"}`}
              style={{ animationDelay: `${i * 95}ms` }}
            >
              {tag}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}
