import { useState } from "react";
import Reveal from "../Reveal.jsx";
import { ArrowUp } from "./icons.jsx";

const PLACEHOLDER =
  "When a customer sends a message on Instagram, classify their intent and if they " +
  "want to buy something, add them to Google Sheets and notify me on Telegram.";

export default function Hero() {
  const [value, setValue] = useState("");
  const submit = () => console.log("FlowForge generate request:", value);
  const onKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); submit(); }
  };

  return (
    <section id="top" className="relative flex min-h-screen items-center justify-center overflow-hidden px-6 pt-16">
      {/* Full-bleed hero art, hue-shifted so the arrow reads cyan, breathing softly. */}
      <img
        src="/assets/hero-paths.png" alt="" aria-hidden="true"
        className="animate-breathe pointer-events-none absolute left-1/2 top-1/2 w-[min(1500px,180%)] max-w-none -translate-x-1/2 -translate-y-[58%] select-none"
        style={{ filter: "hue-rotate(-84deg) saturate(1.1) brightness(1.05)",
          WebkitMaskImage: "radial-gradient(60% 60% at 50% 50%, #000 30%, transparent 80%)",
          maskImage: "radial-gradient(60% 60% at 50% 50%, #000 30%, transparent 80%)" }}
      />

      {/* Soft ink scrim so text stays crisp over the bright artwork. */}
      <div aria-hidden="true" className="pointer-events-none absolute inset-0"
        style={{ background: "radial-gradient(50% 42% at 50% 42%, rgba(5,5,8,0.72), transparent 75%)" }} />

      <div className="relative z-10 mx-auto flex w-full max-w-3xl flex-col items-center text-center">
        <Reveal as="span" className="inline-flex items-center rounded-full border border-white/10 bg-white/[0.03] px-4 py-1.5 text-xs font-medium tracking-wide text-zinc-300 backdrop-blur-sm">
          Open source · Self hosted
        </Reveal>

        <Reveal as="h1" delay={90} className="mt-8 text-balance text-4xl font-semibold leading-[1.08] tracking-tight text-zinc-50 sm:text-6xl">
          Describe your automation.
          <br />
          <span className="text-zinc-400">Receive a workflow that runs.</span>
        </Reveal>

        <Reveal as="p" delay={200} className="mt-7 max-w-2xl text-pretty text-base leading-relaxed text-zinc-400 sm:text-lg">
          FlowForge is your local n8n copilot. A Gemma model, fine tuned on thousands of real
          workflows, turns plain language into automations that run on hardware you own.
        </Reveal>

        <Reveal delay={320} className="group relative mt-11 w-full max-w-2xl">
          {/* Looping ambient glow: a slow conic sweep plus a soft field, both
              brightening on hover and focus. This is the "loop" behind the input. */}
          <div aria-hidden="true" className="pointer-events-none absolute -inset-6 -z-10">
            <div className="animate-spin-slow absolute inset-0 rounded-[2rem] opacity-40 blur-2xl transition-opacity duration-500 group-hover:opacity-90 group-focus-within:opacity-100"
              style={{ background: "conic-gradient(from 0deg, transparent, rgba(56,189,248,0.55), transparent 55%)" }} />
            <div className="animate-breathe absolute inset-4 rounded-[2rem] blur-2xl"
              style={{ background: "radial-gradient(60% 60% at 50% 50%, rgba(56,189,248,0.18), transparent)" }} />
          </div>

          <label htmlFor="hero-input" className="sr-only">Describe the automation you want to build</label>
          <div className="relative rounded-2xl border border-white/10 bg-ink-900/80 p-2 backdrop-blur-md transition-colors duration-300 focus-within:border-accent/70">
            <textarea
              id="hero-input" value={value} onChange={(e) => setValue(e.target.value)} onKeyDown={onKeyDown} rows={3}
              placeholder={PLACEHOLDER}
              className="block w-full resize-none bg-transparent px-4 py-3 pr-14 text-left text-[15px] leading-relaxed text-zinc-100 placeholder:text-zinc-500 focus:outline-none"
            />
            <button type="button" onClick={submit} aria-label="Generate workflow"
              className="absolute bottom-4 right-4 inline-flex h-10 w-10 cursor-pointer items-center justify-center rounded-full bg-accent text-ink-950 shadow-[0_0_20px_rgba(56,189,248,0.5)] transition-all duration-300 hover:bg-accent-light hover:shadow-[0_0_28px_rgba(56,189,248,0.8)]">
              <ArrowUp />
            </button>
          </div>
          <p className="mt-4 text-sm text-zinc-500">Free while in beta. Your prompts never leave your machine.</p>
        </Reveal>
      </div>
    </section>
  );
}
