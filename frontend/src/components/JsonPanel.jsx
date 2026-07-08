// Monospace JSON panel with copy button. The hero UI element of the tool pages.
import { useState } from "react";

export default function JsonPanel({ value, maxHeight = "28rem" }) {
  const [copied, setCopied] = useState(false);
  const text = typeof value === "string" ? value : JSON.stringify(value, null, 2);

  const copy = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1200);
  };

  return (
    <div className="relative rounded-xl border border-white/[0.08] bg-ink-850">
      <button
        onClick={copy}
        className="absolute right-3 top-3 z-10 cursor-pointer rounded-md border border-white/10 px-2.5 py-1 text-xs text-zinc-300 transition-colors duration-200 hover:bg-white/[0.06]"
      >
        {copied ? "Copied" : "Copy"}
      </button>
      <pre
        className="overflow-auto p-4 pt-10 font-mono text-[13px] leading-relaxed text-zinc-200"
        style={{ maxHeight }}
      >
        {text}
      </pre>
    </div>
  );
}
