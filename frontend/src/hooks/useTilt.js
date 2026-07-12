import { useEffect, useRef } from "react";

// Weighted 3D tilt that follows the cursor and springs back on leave.
// rAF-throttled: mousemove only stores coordinates, one transform write per
// frame. Attach the returned ref to an element with the .tilt class.
export function useTilt({ max = 9, scale = 1.02 } = {}) {
  const ref = useRef(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    let frame = 0;
    let pointer = null;

    const render = () => {
      frame = 0;
      if (!pointer) return;
      const r = el.getBoundingClientRect();
      const px = (pointer.x - r.left) / r.width - 0.5;
      const py = (pointer.y - r.top) / r.height - 0.5;
      el.style.transform =
        `perspective(900px) rotateX(${(-py * max).toFixed(2)}deg) ` +
        `rotateY(${(px * max).toFixed(2)}deg) scale(${scale})`;
    };

    const onMove = (e) => {
      pointer = { x: e.clientX, y: e.clientY };
      if (!frame) frame = requestAnimationFrame(render);
    };
    const onLeave = () => {
      pointer = null;
      el.style.transform = "";
    };

    el.addEventListener("mousemove", onMove);
    el.addEventListener("mouseleave", onLeave);
    return () => {
      el.removeEventListener("mousemove", onMove);
      el.removeEventListener("mouseleave", onLeave);
      if (frame) cancelAnimationFrame(frame);
    };
  }, [max, scale]);

  return ref;
}
