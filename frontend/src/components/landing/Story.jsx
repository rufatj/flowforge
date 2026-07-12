import { useEffect, useRef } from "react";
import Reveal from "../Reveal.jsx";
import Eyebrow from "./Eyebrow.jsx";

// A soft studio light that leans toward the cursor: the portrait drifts a
// few pixels away from the pointer and a cyan glow slides beneath it, so the
// frameless image feels touchable instead of pasted in place.
function usePortraitLight() {
  const wrapRef = useRef(null);
  const imgRef = useRef(null);
  const glowRef = useRef(null);

  useEffect(() => {
    const wrap = wrapRef.current;
    const img = imgRef.current;
    const glow = glowRef.current;
    if (!wrap || !img) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    let frame = 0;
    let pointer = null;

    const render = () => {
      frame = 0;
      if (!pointer) return;
      const r = wrap.getBoundingClientRect();
      const px = (pointer.x - r.left) / r.width - 0.5;
      const py = (pointer.y - r.top) / r.height - 0.5;
      img.style.transform = `translate3d(${(-px * 12).toFixed(2)}px, ${(-py * 12).toFixed(2)}px, 0) scale(1.05)`;
      if (glow) {
        glow.style.opacity = "1";
        glow.style.background =
          `radial-gradient(220px circle at ${((px + 0.5) * 100).toFixed(1)}% ${((py + 0.5) * 100).toFixed(1)}%, rgba(125,211,252,0.4), transparent 70%)`;
      }
    };
    const onMove = (e) => {
      pointer = { x: e.clientX, y: e.clientY };
      if (!frame) frame = requestAnimationFrame(render);
    };
    const onLeave = () => {
      pointer = null;
      img.style.transform = "";
      if (glow) glow.style.opacity = "0";
    };

    wrap.addEventListener("mousemove", onMove);
    wrap.addEventListener("mouseleave", onLeave);
    return () => {
      wrap.removeEventListener("mousemove", onMove);
      wrap.removeEventListener("mouseleave", onLeave);
      if (frame) cancelAnimationFrame(frame);
    };
  }, []);

  return { wrapRef, imgRef, glowRef };
}

export default function Story() {
  const { wrapRef, imgRef, glowRef } = usePortraitLight();

  return (
    <section id="story" className="scroll-mt-24 py-28">
      <div className="mx-auto max-w-6xl px-6">
        <div className="grid items-center gap-16 md:grid-cols-[minmax(0,380px)_1fr]">
          <Reveal className="relative mx-auto w-full max-w-sm">
            <div aria-hidden="true" className="absolute inset-0 -z-10 blur-3xl"
              style={{ background: "radial-gradient(50% 50% at 50% 45%, rgba(56,189,248,0.16), transparent)" }} />
            <div ref={wrapRef} className="relative aspect-[4/5] w-full">
              <img
                ref={imgRef}
                src="/assets/human-face.gif"
                alt="A portrait, for the people behind FlowForge"
                className="mask-blend h-full w-full select-none object-cover transition-transform duration-500 ease-out will-change-transform"
              />
              <div
                ref={glowRef}
                aria-hidden="true"
                className="mask-blend pointer-events-none absolute inset-0 opacity-0 mix-blend-screen transition-opacity duration-500"
              />
            </div>
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
