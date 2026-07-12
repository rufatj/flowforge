import { useEffect, useRef } from "react";

// Living background: two drifting cyan light fields that also lean gently
// toward the cursor (rAF-lerped, transform-only), plus grain and a vignette.
export default function AuroraBackground() {
  const blobA = useRef(null);
  const blobB = useRef(null);

  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    let raf = 0;
    const target = { x: 0, y: 0 };
    const pos = { x: 0, y: 0 };

    const loop = () => {
      pos.x += (target.x - pos.x) * 0.04;
      pos.y += (target.y - pos.y) * 0.04;
      // The keyframe animation owns `transform`; parallax writes translate on
      // the wrapper elements instead, so the two never fight.
      if (blobA.current) blobA.current.style.translate = `${pos.x * 46}px ${pos.y * 34}px`;
      if (blobB.current) blobB.current.style.translate = `${-pos.x * 60}px ${-pos.y * 44}px`;
      raf = requestAnimationFrame(loop);
    };
    const onMove = (e) => {
      target.x = e.clientX / window.innerWidth - 0.5;
      target.y = e.clientY / window.innerHeight - 0.5;
    };

    window.addEventListener("mousemove", onMove, { passive: true });
    raf = requestAnimationFrame(loop);
    return () => {
      window.removeEventListener("mousemove", onMove);
      cancelAnimationFrame(raf);
    };
  }, []);

  return (
    <div aria-hidden="true" className="pointer-events-none fixed inset-0 -z-10 overflow-hidden bg-ink-950">
      <div ref={blobA} className="absolute -top-1/3 left-1/4 h-[70vh] w-[70vh]">
        <div className="animate-aurora h-full w-full rounded-full blur-3xl"
          style={{ background: "radial-gradient(circle, rgba(56,189,248,0.16), transparent 60%)" }} />
      </div>
      <div ref={blobB} className="absolute -right-1/4 top-1/2 h-[80vh] w-[80vh]">
        <div className="animate-aurora h-full w-full rounded-full blur-3xl"
          style={{ background: "radial-gradient(circle, rgba(14,165,233,0.12), transparent 60%)", animationDelay: "-13s" }} />
      </div>
      <div className="absolute inset-0 opacity-[0.03]"
        style={{ backgroundImage: "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='2'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")" }} />
      <div className="absolute inset-x-0 top-0 h-64"
        style={{ background: "linear-gradient(to bottom, rgba(56,189,248,0.05), transparent)" }} />
    </div>
  );
}
