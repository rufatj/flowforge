import { useEffect, useRef } from "react";

// Scroll-linked rotation: as the element travels from the bottom of the
// viewport up to the vertical center, it completes its spin and settles.
// Motion is driven purely by scroll position (stops when scrolling stops)
// and never runs past the settle point. Transform-only, rAF-throttled.
export function useScrollSpin({ turns = 0.55, fromScale = 0.82 } = {}) {
  const ref = useRef(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    let frame = 0;
    let isVisible = false;

    const render = () => {
      const rect = el.getBoundingClientRect();
      const vh = window.innerHeight;
      const travel = vh / 2 + rect.height / 2;      // entry -> center distance
      const p = Math.min(1, Math.max(0, (vh - rect.top) / travel));
      const eased = 1 - Math.pow(1 - p, 3);          // ease-out settle
      const angle = (1 - eased) * turns * 360;
      const scale = fromScale + (1 - fromScale) * eased;
      
      el.style.transform = `rotate(${angle.toFixed(2)}deg) scale(${scale.toFixed(3)})`;
      el.style.opacity = (0.25 + 0.75 * eased).toFixed(3);

      if (isVisible) {
        frame = requestAnimationFrame(render);
      }
    };

    // Since window doesn't scroll in fullpage mode, we run a continuous render
    // loop while the element is anywhere inside the viewport. This syncs perfectly
    // with the CSS transform transition of the fullpage slide.
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          isVisible = true;
          if (!frame) frame = requestAnimationFrame(render);
        } else {
          isVisible = false;
          if (frame) {
            cancelAnimationFrame(frame);
            frame = 0;
          }
        }
      });
    }, { rootMargin: "0px", threshold: 0 });

    observer.observe(el);

    return () => {
      observer.disconnect();
      isVisible = false;
      if (frame) cancelAnimationFrame(frame);
    };
  }, [turns, fromScale]);

  return ref;
}
