// Grouped bar chart: per-gate pass rate, base vs fine-tuned.
// Series colors are validated for the dark surface with the dataviz
// six-checks validator (CVD dE 40+, contrast >= 3:1, lightness band).
import {
  Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";

export const BASE_COLOR = "#a16207"; // bronze: baseline series
export const FT_COLOR = "#0284c7";   // sky: fine-tuned series

export default function GateChart({ data }) {
  return (
    <div className="rounded-2xl border border-white/[0.07] bg-white/[0.02] p-6">
      <h2 className="text-sm font-medium text-zinc-300">Gate pass rate, percent</h2>
      <div className="mt-4 h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} barGap={2} barCategoryGap="28%">
            <CartesianGrid stroke="rgba(255,255,255,0.05)" vertical={false} />
            <XAxis dataKey="gate" tick={{ fill: "#a1a1aa", fontSize: 12 }} axisLine={false} tickLine={false} />
            <YAxis domain={[0, 100]} tick={{ fill: "#71717a", fontSize: 11 }} axisLine={false} tickLine={false} width={32} />
            <Tooltip
              cursor={{ fill: "rgba(255,255,255,0.04)" }}
              contentStyle={{ background: "#101017", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, color: "#e4e4e7", fontSize: 12 }}
              formatter={(v) => (v == null ? "pending" : `${v}%`)}
            />
            <Legend wrapperStyle={{ fontSize: 12, color: "#a1a1aa" }} />
            <Bar dataKey="base" name="Base Gemma" fill={BASE_COLOR} radius={[4, 4, 0, 0]} maxBarSize={44} isAnimationActive={false} />
            <Bar dataKey="ft" name="Fine-tuned" fill={FT_COLOR} radius={[4, 4, 0, 0]} maxBarSize={44} isAnimationActive={false} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
