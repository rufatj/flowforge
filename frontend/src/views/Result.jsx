// Result: import the generated workflow into n8n and try its webhook live.
import { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api.js";
import { loadGeneration } from "../store.js";
import JsonPanel from "../components/JsonPanel.jsx";

export default function Result() {
  const generation = loadGeneration();
  const [imported, setImported] = useState(null);
  const [formHtml, setFormHtml] = useState(null);
  const [busy, setBusy] = useState(null); // "import" | "form" | null
  const [error, setError] = useState(null);

  const run = async (kind, fn) => {
    setBusy(kind);
    setError(null);
    try {
      await fn();
    } catch (e) {
      setError(String(e.message || e));
    } finally {
      setBusy(null);
    }
  };

  if (!generation?.workflow) {
    return (
      <div className="mx-auto max-w-3xl space-y-4">
        <h1 className="text-3xl font-semibold tracking-tight text-zinc-50">Result</h1>
        <p className="text-zinc-400">Nothing generated yet in this session.</p>
        <Link to="/generate" className="inline-flex cursor-pointer rounded-full bg-accent px-5 py-2 text-sm font-medium text-ink-950 hover:bg-accent-light transition-colors duration-200">
          Generate a workflow first
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl space-y-8">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight text-zinc-50">Your workflow</h1>
        <p className="mt-2 text-zinc-400">"{generation.description}"</p>
      </div>

      <div className="flex flex-wrap gap-3">
        <button
          onClick={() => run("import", async () => setImported(await api.importWorkflow(generation.workflow)))}
          disabled={busy !== null}
          className="cursor-pointer rounded-full bg-accent px-5 py-2 text-sm font-medium text-ink-950 transition-colors duration-200 hover:bg-accent-light disabled:opacity-40"
        >
          {busy === "import" ? "Importing…" : "Import to n8n"}
        </button>
        <button
          onClick={() => run("form", async () => setFormHtml(await api.testform(generation.workflow)))}
          disabled={busy !== null}
          className="cursor-pointer rounded-full border border-white/15 px-5 py-2 text-sm font-medium text-zinc-200 transition-colors duration-200 hover:border-white/30 hover:bg-white/[0.03] disabled:opacity-40"
        >
          {busy === "form" ? "Building…" : "Create test form"}
        </button>
      </div>

      {error && (
        <div className="rounded-xl border border-red-500/30 bg-red-500/[0.06] p-4 text-sm text-red-300">{error}</div>
      )}

      {imported && (
        <div className="space-y-2 rounded-xl border border-emerald-500/25 bg-emerald-500/[0.05] p-5 text-sm">
          <p className="text-emerald-300">Imported. {imported.node_count} nodes now live in your n8n.</p>
          <a href={imported.editor_url} target="_blank" rel="noreferrer" className="text-accent hover:text-accent-light transition-colors duration-200">
            Open in the n8n editor →
          </a>
          {imported.webhook_urls?.map((u) => (
            <p key={u} className="font-mono text-xs text-zinc-400">webhook: {u}</p>
          ))}
        </div>
      )}

      {formHtml && (
        <div className="overflow-hidden rounded-xl border border-white/[0.08]">
          <iframe title="Webhook test form" srcDoc={formHtml} className="h-[460px] w-full bg-ink-950" />
        </div>
      )}

      <JsonPanel value={generation.workflow} maxHeight="22rem" />
    </div>
  );
}
