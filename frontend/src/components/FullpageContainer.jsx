import { useFullpage } from "../hooks/useFullpage.js";

/**
 * FullpageContainer
 *
 * Wraps an array of React elements as full-viewport sections.
 * Right-rail nav: thin vertical dashes — active dash stretches and glows.
 * Automatically synchronizes with anchors array for URL hashes.
 */
export default function FullpageContainer({
  sections = [],
  anchors = [],
  duration = 900,
  showDots = true,
}) {
  const count = sections.length;
  // Pass anchors directly to hook instead of just count
  const { current, go } = useFullpage(anchors, { duration });

  const translateY = `translateY(calc(${current} * -100vh))`;

  return (
    <div className="relative h-screen overflow-hidden">
      {/* Slide stack */}
      <div
        className="will-change-transform"
        style={{
          transform: translateY,
          transition: `transform ${duration}ms cubic-bezier(0.77, 0, 0.175, 1)`,
        }}
      >
        {sections.map((section, i) => (
          <div
            key={i}
            className="relative flex h-screen w-screen flex-col overflow-hidden"
            aria-hidden={i !== current}
          >
            {section}
          </div>
        ))}
      </div>

      {/* ── Right-rail nav ── */}
      {showDots && (
        <nav
          aria-label="Page navigation"
          className="fp-nav group/nav fixed right-5 top-1/2 z-50 flex -translate-y-1/2 flex-col items-end gap-[10px]"
        >
          {sections.map((_, i) => {
            const active = i === current;
            return (
              <button
                key={i}
                aria-label={`Section ${i + 1}`}
                onClick={() => go(i)}
                className="fp-nav-btn relative flex items-center justify-end gap-2 py-1 pr-0"
                style={{ outline: "none" }}
              >
                {/* Dash bar */}
                <span
                  className="fp-dash block rounded-full transition-all"
                  style={{
                    width: active ? "28px" : "12px",
                    height: "2px",
                    background: active
                      ? "rgba(56,189,248,0.95)"
                      : "rgba(255,255,255,0.2)",
                    boxShadow: active
                      ? "0 0 8px 1px rgba(56,189,248,0.55)"
                      : "none",
                    transitionDuration: "500ms",
                    transitionTimingFunction: "cubic-bezier(0.22,1,0.36,1)",
                  }}
                />
              </button>
            );
          })}
        </nav>
      )}

      {/* Section counter — bottom-left */}
      <div className="pointer-events-none fixed bottom-6 left-6 z-50 select-none font-mono text-[11px] text-zinc-600">
        <span className="text-zinc-400">{String(current + 1).padStart(2, "0")}</span>
        <span className="mx-1 text-zinc-600">/</span>
        {String(count).padStart(2, "0")}
      </div>

      {/* Scroll hint — first slide only */}
      {current === 0 && (
        <div className="pointer-events-none fixed bottom-6 left-1/2 z-50 flex -translate-x-1/2 flex-col items-center gap-1.5">
          <span className="text-[10px] uppercase tracking-[0.3em] text-zinc-600">scroll</span>
          <span
            className="block h-5 w-px rounded-full"
            style={{
              background: "linear-gradient(to bottom, rgba(56,189,248,0.6), transparent)",
              animation: "scroll-hint-fade 1.8s ease-in-out infinite",
            }}
          />
        </div>
      )}
    </div>
  );
}
