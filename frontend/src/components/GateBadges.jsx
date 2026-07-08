// Pass/fail chips for the three eval gates. Muted red for fail, cyan-green for pass.

function Badge({ ok, children }) {
  const cls = ok
    ? "border-emerald-500/40 text-emerald-400"
    : "border-red-500/30 text-red-400/80";
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium ${cls}`}>
      {children} {ok ? "✓" : "✗"}
    </span>
  );
}

export default function GateBadges({ gates }) {
  if (!gates) return null;
  return (
    <div className="flex flex-wrap gap-2">
      <Badge ok={gates.json_valid}>JSON valid</Badge>
      <Badge ok={gates.schema_valid}>Schema valid</Badge>
      {"import_valid" in gates && <Badge ok={gates.import_valid}>Imports</Badge>}
    </div>
  );
}
