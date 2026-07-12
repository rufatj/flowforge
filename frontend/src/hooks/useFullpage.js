import { useEffect, useRef, useState, useCallback } from "react";

/**
 * useFullpage — intercepts wheel / touch / keyboard events and translates the
 * container so each "section" occupies exactly one viewport height.
 * Synchronizes browser hash routing for professional, bookmarkable page states.
 *
 * @param {string[]} anchors Array of URL hashes (e.g. ['#top', '#how', ...]).
 * @param {object} options
 *   @param {number} options.duration   Transition duration in ms (default 900).
 *   @param {boolean} options.disabled  Skip fullpage behaviour entirely.
 */
export function useFullpage(anchors, { duration = 900, disabled = false } = {}) {
  const count = anchors.length;

  const getHashIndex = useCallback(() => {
    const hash = window.location.hash;
    const idx = anchors.indexOf(hash);
    return idx !== -1 ? idx : 0;
  }, [anchors]);

  const [current, setCurrent] = useState(getHashIndex);
  const busy = useRef(false);        // debounce: ignore events while animating
  const touchY = useRef(null);

  const go = useCallback(
    (nextIndex) => {
      if (disabled || busy.current) return;
      const clamped = Math.max(0, Math.min(count - 1, nextIndex));
      if (clamped === current) return;
      
      busy.current = true;
      window.location.hash = anchors[clamped];
      
      setTimeout(() => {
        busy.current = false;
      }, duration + 50);
    },
    [count, current, disabled, duration, anchors]
  );

  const prev = useCallback(() => go(current - 1), [go, current]);
  const next = useCallback(() => go(current + 1), [go, current]);

  // Handle URL updates & back/forward navigation
  useEffect(() => {
    if (disabled) return;
    
    const onHashChange = () => {
      const hash = window.location.hash;
      const idx = anchors.indexOf(hash);
      const targetIdx = idx !== -1 ? idx : 0;
      
      if (targetIdx !== current) {
        busy.current = true;
        setCurrent(targetIdx);
        setTimeout(() => {
          busy.current = false;
        }, duration + 50);
      }
    };

    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, [anchors, current, disabled, duration]);

  /* ── wheel ── */
  useEffect(() => {
    if (disabled) return;
    const onWheel = (e) => {
      e.preventDefault();
      if (e.deltaY > 0) next();
      else prev();
    };
    window.addEventListener("wheel", onWheel, { passive: false });
    return () => window.removeEventListener("wheel", onWheel);
  }, [disabled, next, prev]);

  /* ── touch ── */
  useEffect(() => {
    if (disabled) return;
    const onStart = (e) => { touchY.current = e.touches[0].clientY; };
    const onEnd = (e) => {
      if (touchY.current === null) return;
      const delta = touchY.current - e.changedTouches[0].clientY;
      if (Math.abs(delta) > 40) { delta > 0 ? next() : prev(); }
      touchY.current = null;
    };
    window.addEventListener("touchstart", onStart, { passive: true });
    window.addEventListener("touchend", onEnd, { passive: true });
    return () => {
      window.removeEventListener("touchstart", onStart);
      window.removeEventListener("touchend", onEnd);
    };
  }, [disabled, next, prev]);

  /* ── keyboard ── */
  useEffect(() => {
    if (disabled) return;
    const onKey = (e) => {
      if (["ArrowDown", "PageDown", "Space"].includes(e.code)) { e.preventDefault(); next(); }
      if (["ArrowUp", "PageUp"].includes(e.code)) { e.preventDefault(); prev(); }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [disabled, next, prev]);

  return { current, go };
}
