"use client";

import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";
import type { GapSummary } from "@/lib/api";

const categoryColor = (index: number) => {
  if (index >= 60) return "#EF4444";
  if (index >= 30) return "#F59E0B";
  return "#22C55E";
};

export default function OccupationRanking({ data }: { data: GapSummary[] }) {
  const top = [...data].sort((a, b) => b.avg_talent_gap_index - a.avg_talent_gap_index).slice(0, 8);

  return (
    <div className="bg-gray-900 rounded-2xl p-6">
      <h2 className="text-white font-semibold text-lg mb-1">Top Occupations by Gap Index</h2>
      <p className="text-gray-400 text-sm mb-4">AI-adjacent occupations ranked by average Talent Gap Index</p>
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={top} layout="vertical" margin={{ top: 0, right: 16, left: 8, bottom: 0 }}>
          <XAxis type="number" domain={[0, 100]} stroke="#9CA3AF" tick={{ fontSize: 11 }} />
          <YAxis
            type="category"
            dataKey="occupation"
            width={180}
            stroke="#9CA3AF"
            tick={{ fontSize: 11, fill: "#D1D5DB" }}
            tickFormatter={(v: string) => v.length > 28 ? v.slice(0, 28) + "…" : v}
          />
          <Tooltip
            contentStyle={{ backgroundColor: "#1F2937", border: "none", borderRadius: 8 }}
            labelStyle={{ color: "#F9FAFB" }}
            formatter={(v: unknown) => [(v as number).toFixed(1), "Gap Index"]}
          />
          <Bar dataKey="avg_talent_gap_index" radius={[0, 4, 4, 0]}>
            {top.map((entry, i) => (
              <Cell key={i} fill={categoryColor(entry.avg_talent_gap_index)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div className="flex gap-4 mt-3 text-xs text-gray-400">
        <span><span className="inline-block w-2 h-2 rounded-full bg-red-500 mr-1" />Critical (&gt;60)</span>
        <span><span className="inline-block w-2 h-2 rounded-full bg-yellow-500 mr-1" />Moderate (30–60)</span>
        <span><span className="inline-block w-2 h-2 rounded-full bg-green-500 mr-1" />Low (&lt;30)</span>
      </div>
    </div>
  );
}
