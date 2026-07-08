// Generate: describe an automation, get validated n8n workflow JSON.
// Same input styling as the landing hero. On success, offers the Result step.
import { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api.js";
import { saveGeneration } from "../store.js";
import JsonPanel from "../components/JsonPanel.jsx";
import GateBadges from "../components/GateBadges.jsx";

const PLACEHOLDER =
  "When a customer sends a message on Instagram, classify their intent and if they " +
  "want to buy something, add them to Google Sheets and notify me on Telegram.";

export default function Generate() {
  const [description, setDescription] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const onGenerate = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const r = await api.generate(description);
      setResult(r);
      saveGeneration({ description, ...r });
    } catch (e) {
      setError(String(e.message || e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-3xl space-y-8">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight text-zinc-50">Describe your automation</h1>
        <p className="mt-2 text-zinc-400">Plain language in, an importable n8n workflow out.</p>
      </div>

      <div className="group relative rounded-2xl border border-white/10 bg-white/[0.03] p-2 transition-colors duration-200 focus-within:border-accent">
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={4}
          placeholder={PLACEHOLDER}
          className="block w-full resize-none bg-transparent px-4 py-3 text-[15px] leading-relaxed text-zinc-100 placeholder:text-zinc-500 focus:outline-none"
        />
        <div className="flex items-center justify-between px-4 pb-2">
          <span className="text-xs text-zinc-600">Runs on your own model endpoint.</span>
          <button
            onClick={onGenerate}
            disabled={loading || description.trim().length < 3}
            className="cursor-pointer rounded-full bg-accent px-5 py-2 text-sm font-medium text-ink-950 transition-colors duration-200 hover:bg-accent-light disabled:cursor-default disabled:opacity-40"
          >
            {loading ? "Generating…" : "Generate workflow"}
          </button>
        </div>
      </div>

      {loading && (
        <div className="rounded-xl border border-white/[0.07] bg-white/[0.02] p-6 text-sm text-zinc-400">
          The model is writing your workflow. This usually takes a few seconds.
        </div>
      )}

      {error && (
        <div className="rounded-xl border border-red-500/30 bg-red-500/[0.06] p-4 text-sm text-red-300">
          {error}
        </div>
      )}

      {result && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <GateBadges gates={result.gates} />
            <span className="text-xs text-zinc-600">
              {result.attempts > 1 ? "took a retry" : "first try"}
            </span>
          </div>
          {result.errors?.length > 0 && (
            <div className="rounded-xl border border-amber-500/25 bg-amber-500/[0.05] p-4 text-xs text-amber-200/90">
              {result.errors.slice(0, 4).map((e, i) => <div key={i}>{e}</div>)}
            </div>
          )}
          <JsonPanel value={result.workflow ?? result.raw} />
          {result.gates?.schema_valid && (
            <Link
              to="/result"
              className="inline-flex cursor-pointer rounded-full bg-accent px-5 py-2 text-sm font-medium text-ink-950 transition-colors duration-200 hover:bg-accent-light"
            >
              Continue to import →
            </Link>
          )}
        </div>
      )}
    </div>
  );
}
