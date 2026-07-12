import { useMemo, useState } from "react";
import Reveal from "../Reveal.jsx";
import { useTypewriter } from "../../hooks/useTypewriter.js";
import { ArrowUp } from "./icons.jsx";

const EXAMPLE_PROMPTS = [
  "When a customer sends a message on Instagram, classify their intent and if they want to buy something, add them to Google Sheets and notify me on Telegram.",
  "Every morning at eight, collect yesterday's Stripe payments and post a revenue summary to my Slack channel.",
  "When someone fills the contact form on my site, enrich their email with Clearbit and create a lead in HubSpot.",
  "Watch this RSS feed and whenever a new article mentions my brand, summarize it with AI and email me the digest.",
  "When a new row appears in my Google Sheet, generate an invoice PDF and send it to the client through Gmail.",
  "If a customer leaves a one star review, open a ticket in Linear and alert the support team on Discord.",
  "Every Friday, pull my unpaid invoices from Notion, remind each client by email, and log who was contacted.",
];

export default function Hero() {
  const [value, setValue] = useState("");
  const [focused, setFocused] = useState(false);
  const [launching, setLaunching] = useState(false);

  // The typewriter runs only while the field is untouched.
  const idle = !focused && value.length === 0;
  const ghost = useTypewriter(useMemo(() => EXAMPLE_PROMPTS, []), idle);

  const submit = () => {
    if (launching) return;
    console.log("FlowForge generate request:", value);
    setLaunching(true);
    setTimeout(() => setLaunching(false), 950);
  };
  const onKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); submit(); }
  };

  return (
    <section id="top" className="relative flex min-h-screen items-center justify-center overflow-hidden px-6 pt-16">
      {/* Full-bleed hero art, hue-shifted to cyan, breathing softly. */}
      <img
        src="/assets/hero-paths.png" alt="" aria-hidden="true"
        className="animate-breathe pointer-events-none absolute left-1/2 top-1/2 w-[min(1500px,180%)] max-w-none -translate-x-1/2 -translate-y-[58%] select-none"
        style={{ filter: "hue-rotate(-84deg) saturate(1.1) brightness(1.05)",
          WebkitMaskImage: "radial-gradient(60% 60% at 50% 50%, #000 30%, transparent 80%)",
          maskImage: "radial-gradient(60% 60% at 50% 50%, #000 30%, transparent 80%)" }}
      />
      {/* Ink scrim keeps type crisp over the artwork. */}
      <div aria-hidden="true" className="pointer-events-none absolute inset-0"
        style={{ background: "radial-gradient(52% 44% at 50% 46%, rgba(5,5,8,0.74), transparent 75%)" }} />

      <div className="relative z-10 mx-auto flex w-full max-w-3xl flex-col items-center text-center">
        <Reveal as="h1" className="text-balance text-4xl font-semibold leading-[1.08] tracking-tight text-zinc-50 sm:text-6xl">
          Describe your automation.
          <br />
          <span className="text-zinc-300">Receive a workflow that runs.</span>
        </Reveal>

        <Reveal as="p" delay={160} className="mt-7 max-w-2xl text-pretty text-base leading-relaxed text-zinc-400 sm:text-lg">
          FlowForge is your local n8n copilot. A Gemma model, fine tuned on thousands of real
          workflows, turns plain language into automations that run on hardware you own.
        </Reveal>

        {/* The centerpiece: idea in, workflow out. */}
        <Reveal delay={300} className="group relative mt-12 w-full max-w-2xl rounded-2xl p-[1.5px]">
          {/* Thin light arc orbiting the frame on hover/focus. */}
          <div aria-hidden="true" className="beam-layer" />
          {/* Faint resting rim so the beam has a track to travel. */}
          <div aria-hidden="true" className="pointer-events-none absolute inset-0 rounded-2xl border border-white/10 transition-colors duration-300 group-focus-within:border-accent/40" />

          <div className="relative rounded-[calc(1rem-1px)] bg-ink-900/85 p-2 backdrop-blur-md">
            <label htmlFor="hero-input" className="sr-only">Describe the automation you want to build</label>
            <div className="relative">
              <textarea
                id="hero-input" value={value} rows={3}
                onChange={(e) => setValue(e.target.value)} onKeyDown={onKeyDown}
                onFocus={() => setFocused(true)} onBlur={() => setFocused(false)}
                className="block w-full resize-none bg-transparent px-4 py-3 pr-14 text-left text-[15px] leading-relaxed text-zinc-100 caret-accent focus:outline-none"
              />
              {/* Rotating example prompts, typed live with a caret. */}
              {idle && (
                <div aria-hidden="true" className="pointer-events-none absolute inset-0 px-4 py-3 pr-14 text-left text-[15px] leading-relaxed text-zinc-500">
                  {ghost}
                  <span className="animate-caret ml-px inline-block h-[1.1em] w-[2px] translate-y-[3px] bg-accent/80" />
                </div>
              )}
            </div>
            <button type="button" onClick={submit} aria-label="Generate workflow"
              className="absolute bottom-4 right-4 inline-flex h-10 w-10 cursor-pointer items-center justify-center overflow-hidden rounded-full bg-accent text-ink-950 shadow-[0_0_20px_rgba(56,189,248,0.45)] transition-all duration-300 hover:bg-accent-light hover:shadow-[0_0_30px_rgba(56,189,248,0.75)]">
              <ArrowUp className={`h-5 w-5 ${launching ? "animate-rocket" : ""}`} />
            </button>
          </div>
        </Reveal>

        <Reveal as="p" delay={420} className="mt-5 text-sm text-zinc-500">
          Free while in beta. Your prompts never leave your machine.
        </Reveal>
      </div>
    </section>
  );
}
