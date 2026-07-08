import Reveal from "../Reveal.jsx";
import Eyebrow from "./Eyebrow.jsx";

// The hand image sits in a frameless, edge-lit panel: a soft cyan gradient
// halo behind it, and its own edges masked so it melts into the page.
export default function WhyDifferent() {
  return (
    <section id="why" className="scroll-mt-24 py-28">
      <div className="mx-auto max-w-6xl px-6">
        <div className="grid items-center gap-14 md:grid-cols-2">
          <Reveal className="relative">
            <div aria-hidden="true" className="absolute -inset-8 -z-10 rounded-full opacity-60 blur-3xl"
              style={{ background: "radial-gradient(50% 50% at 50% 50%, rgba(56,189,248,0.14), transparent)" }} />
            <img
              src="/assets/integrations-hand.png"
              alt="A hand reaching toward glowing tiles for Claude, ChatGPT and n8n"
              className="mask-blend w-full select-none"
            />
          </Reveal>

          <div>
            <Eyebrow label="Ownership" title="A copilot that answers only to you" />
            <div className="mt-7 space-y-5 text-[15px] leading-relaxed text-zinc-400">
              <Reveal as="p" delay={60}>
                Most generators ship your prompts to a provider you cannot see. Your logic, your
                schemas, your keys, all of it passes through their servers.
              </Reveal>
              <Reveal as="p" delay={120}>
                FlowForge runs on your own machine. The weights are open. The training data is
                public. The code is yours under an MIT license.
              </Reveal>
              <Reveal as="p" delay={180} className="text-lg font-medium text-zinc-100">
                Nothing leaves. Everything stays.
              </Reveal>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
