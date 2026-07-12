import { useEffect, useRef } from "react";
import Reveal from "../Reveal.jsx";

// Full-screen immersive chapter. The hand artwork fills the viewport behind
// centered copy. A localized ripple effect follows the mouse, using a masked
// SVG displacement field over a duplicated image layer.
function useRipple(containerRef) {
  const turbRef = useRef(null);
  const dispRef = useRef(null);

  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const container = containerRef.current;
    if (!container) return;

    let raf = 0;
    let scale = 0;         // current displacement strength
    let target = 0;        // where it wants to be
    let phase = 0;         // drives the slow churn of the noise field
    
    const loop = () => {
      scale += (target - scale) * (target > scale ? 0.08 : 0.03); // fast in, slow heal
      phase += 0.0022;
      
      if (dispRef.current) dispRef.current.setAttribute("scale", scale.toFixed(2));
      if (turbRef.current && scale > 0.4) {
        const f = 0.011 + Math.sin(phase * 7) * 0.0016;
        turbRef.current.setAttribute("baseFrequency", `${f.toFixed(4)} ${(f * 1.6).toFixed(4)}`);
      }
      
      // Update opacity/scale CSS variable for the rippled layer
      container.style.setProperty("--ripple-scale", (scale / 30).toFixed(3));

      if (scale > 0.05 || target > 0) {
        raf = requestAnimationFrame(loop);
      } else {
        raf = 0;
      }
    };

    const wake = () => {
      if (!raf) raf = requestAnimationFrame(loop);
    };

    const updateMouse = (e) => {
      const rect = container.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      container.style.setProperty("--x", `${x}px`);
      container.style.setProperty("--y", `${y}px`);
    };

    const onEnter = (e) => { 
      target = 30; 
      updateMouse(e);
      wake(); 
    };
    
    const onLeave = () => { 
      target = 0; 
      wake(); 
    };
    
    const onMove = (e) => {
      updateMouse(e);
    };

    container.addEventListener("mouseenter", onEnter);
    container.addEventListener("mouseleave", onLeave);
    container.addEventListener("mousemove", onMove);
    return () => {
      container.removeEventListener("mouseenter", onEnter);
      container.removeEventListener("mouseleave", onLeave);
      container.removeEventListener("mousemove", onMove);
      if (raf) cancelAnimationFrame(raf);
    };
  }, [containerRef]);

  return { turbRef, dispRef };
}

export default function WhyDifferent() {
  const containerRef = useRef(null);
  const { turbRef, dispRef } = useRipple(containerRef);

  return (
    <section id="why" className="relative flex min-h-screen scroll-mt-24 items-center justify-center overflow-hidden py-28">
      {/* The displacement field that liquefies the artwork. */}
      <svg aria-hidden="true" className="absolute h-0 w-0">
        <filter id="ripple-hand">
          <feTurbulence ref={turbRef} type="fractalNoise" baseFrequency="0.011 0.018" numOctaves="2" seed="7" result="noise" />
          <feDisplacementMap ref={dispRef} in="SourceGraphic" in2="noise" scale="0" xChannelSelector="R" yChannelSelector="G" />
        </filter>
      </svg>

      {/* Full-bleed artwork wrapper with the static edge mask applied globally */}
      <div 
        className="absolute inset-0 flex items-center justify-center opacity-70"
        style={{ 
          WebkitMaskImage: "radial-gradient(75% 70% at 50% 50%, #000 40%, transparent 92%)",
          maskImage: "radial-gradient(75% 70% at 50% 50%, #000 40%, transparent 92%)" 
        }}
      >
        <div 
          ref={containerRef}
          className="relative h-full w-full"
          style={{ 
            "--x": "50%", 
            "--y": "50%",
            "--ripple-scale": "0",
          }}
        >
          {/* Base Image (Static) */}
          <img
            src="/assets/integrations-hand.png"
            alt="A hand reaching toward glowing tiles for Claude, ChatGPT and n8n"
            className="absolute inset-0 h-full w-full select-none object-cover"
          />
          
          {/* Rippled Image (Masked to cursor position) */}
          <img
            src="/assets/integrations-hand.png"
            alt=""
            aria-hidden="true"
            className="absolute inset-0 h-full w-full select-none object-cover will-change-transform"
            style={{ 
              filter: "url(#ripple-hand)",
              opacity: "var(--ripple-scale)",
              WebkitMaskImage: "radial-gradient(circle 350px at var(--x) var(--y), black 0%, transparent 100%)",
              maskImage: "radial-gradient(circle 350px at var(--x) var(--y), black 0%, transparent 100%)",
            }}
          />
        </div>
      </div>
      
      {/* Scrim for copy legibility. */}
      <div aria-hidden="true" className="pointer-events-none absolute inset-0"
        style={{ background: "radial-gradient(46% 40% at 50% 52%, rgba(5,5,8,0.78), transparent 80%)" }} />

      {/* Centered copy over the living image. */}
      <div className="pointer-events-none relative z-10 mx-auto max-w-2xl px-6 text-center">
        <Reveal as="span" className="text-[11px] font-medium uppercase tracking-[0.28em] text-accent/80">
          Ownership
        </Reveal>
        <Reveal as="h2" delay={90} className="mt-4 text-3xl font-semibold tracking-tight text-zinc-50 sm:text-5xl">
          A copilot that answers only to you
        </Reveal>
        <Reveal as="p" delay={190} className="mt-7 text-[15px] leading-relaxed text-zinc-300 sm:text-base">
          Most generators ship your prompts to a provider you cannot see. Your logic, your schemas,
          your keys, all of it passes through their servers.
        </Reveal>
        <Reveal as="p" delay={280} className="mt-4 text-[15px] leading-relaxed text-zinc-300 sm:text-base">
          FlowForge runs on your own machine. The weights are open. The training data is public.
          The code is yours under an MIT license.
        </Reveal>
        <Reveal as="p" delay={370} className="mt-7 text-xl font-medium text-zinc-50">
          Nothing leaves. Everything stays.
        </Reveal>
      </div>
    </section>
  );
}
