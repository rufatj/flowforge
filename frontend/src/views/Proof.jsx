// Proof: base model vs fine-tuned, measured by the three-gate harness.
// Reads /results. Renders fine while only the baseline run exists.
import { useEffect, useState } from "react";
import { api } from "../api.js";
import GateBadges from "../components/GateBadges.jsx";
import GateChart, { BASE_COLOR, FT_COLOR } from "../components/GateChart.jsx";

const GATE_LABELS = { gate1: "JSON valid", gate2: "Schema valid", gate3: "Live import" };
const pct = (v) => (v == null ? "—" : `${Math.round(v * 100)}%`);

function pickRuns(runs) {
  const ft = runs.find((r) => /sft|flowforge|tuned/i.test(r.label));
  const base = runs.find((r) => r !== ft) ?? null;
  return { base, ft: ft ?? null };
}

function StatTile({ title, run, color }) {
  return (
    <div className="flex-1 rounded-2xl border border-white/[0.07] bg-white/[0.02] p-6">
      <div className="flex items-center gap-2 text-sm text-zinc-400">
        <span className="h-2.5 w-2.5 rounded-full" style={{ background: color }} />
        {title}
      </div>
      <div className="mt-2 text-4xl font-semibold tracking-tight text-zinc-50">
        {run ? pct(run.gate3) : "pending"}
      </div>
      <div className="mt-1 text-xs text-zinc-500">
        {run ? `live import success · n=${run.total} · ${run.model}` : "runs after AMD fine tuning"}
      </div>
    </div>
  );
}

export default function Proof() {
  const [runs, setRuns] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.results().then((d) => setRuns(d.runs ?? [])).catch((e) => setError(String(e)));
  }, []);

  if (error) return <p className="text-red-400 text-sm">{error}</p>;
  if (runs === null) return <p className="text-zinc-500 text-sm">Loading results…</p>;

  const { base, ft } = pickRuns(runs);
  const chartData = ["gate1", "gate2", "gate3"].map((g) => ({
    gate: GATE_LABELS[g],
    base: base ? Math.round(base[g] * 100) : null,
    ft: ft ? Math.round(ft[g] * 100) : null,
  }));

  return (
    <div className="space-y-10">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight text-zinc-50">Proof</h1>
        <p className="mt-2 max-w-2xl text-zinc-400">
          Every output goes through three gates: JSON parses, the schema matches what n8n
          expects, and a live n8n instance accepts the import. The number that matters is gate three.
        </p>
      </div>

      {runs.length === 0 ? (
        <div className="rounded-2xl border border-white/[0.07] bg-white/[0.02] p-8 text-sm text-zinc-400">
          No eval runs yet. Run <code className="font-mono text-zinc-300">python -m eval.run_eval</code> to
          produce the baseline.
        </div>
      ) : (
        <>
          <div className="flex flex-col gap-4 sm:flex-row">
            <StatTile title="Base Gemma" run={base} color={BASE_COLOR} />
            <StatTile title="FlowForge fine tuned" run={ft} color={FT_COLOR} />
          </div>

          <GateChart data={chartData} />

          {base?.examples?.length > 0 && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-zinc-100">Sample outputs</h2>
              <div className="grid gap-4 md:grid-cols-2">
                {base.examples.slice(0, 4).map((ex, i) => (
                  <div key={i} className="rounded-2xl border border-white/[0.07] bg-white/[0.02] p-5">
                    <p className="text-sm text-zinc-300">"{ex.prompt.slice(0, 140)}{ex.prompt.length > 140 ? "…" : ""}"</p>
                    <div className="mt-3"><GateBadges gates={ex.gates} /></div>
                    <pre className="mt-3 max-h-40 overflow-auto rounded-lg bg-ink-950 p-3 font-mono text-[11px] leading-relaxed text-zinc-400">
                      {ex.output.slice(0, 600) || "(empty output)"}
                    </pre>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
