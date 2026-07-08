import Reveal from "../Reveal.jsx";
import Eyebrow from "./Eyebrow.jsx";

// The portrait plays with no frame. Its near-black backdrop and a radial edge
// mask let it dissolve straight into the page, so it feels present in the room
// rather than pasted into a box. A faint cyan halo gives it depth.
export default function Story() {
  return (
    <section id="story" className="scroll-mt-24 py-28">
      <div className="mx-auto max-w-6xl px-6">
        <div className="grid items-center gap-16 md:grid-cols-[minmax(0,380px)_1fr]">
          <Reveal className="relative mx-auto w-full max-w-sm">
            <div aria-hidden="true" className="absolute inset-0 -z-10 blur-3xl"
              style={{ background: "radial-gradient(50% 50% at 50% 45%, rgba(56,189,248,0.16), transparent)" }} />
            <img
              src="/assets/human-face.gif"
              alt="A portrait, for the people behind FlowForge"
              className="mask-blend aspect-[4/5] w-full select-none object-cover"
            />
          </Reveal>

          <div>
            <Eyebrow label="The reason" title="Why FlowForge exists" />
            <div className="mt-7 space-y-5 text-[15px] leading-relaxed text-zinc-400">
              <Reveal as="p" delay={60}>
                Paid copilots keep your automations behind someone else's login. For a team that
                ships automations every day, that is a running cost and a quiet loss of control.
              </Reveal>
              <Reveal as="p" delay={120}>
                FlowForge is the copilot we wanted for ourselves. Open weights, local inference, and
                evaluation numbers anyone can audit in the open.
              </Reveal>
              <Reveal as="p" delay={180}>
                It is a real model with real results, not a black box. When it misses, you can see
                why and make it sharper. That is the quiet luxury of owning your tools.
              </Reveal>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
