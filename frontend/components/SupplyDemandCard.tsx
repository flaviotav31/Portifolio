"use client";

import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import type { SupplyStats } from "@/lib/api";

const COLORS = ["#A78BFA", "#374151"];

export default function SupplyDemandCard({ stats }: { stats: SupplyStats }) {
  const pieData = [
    { name: "AI-related graduates", value: Math.round(stats.ai_graduates_per_year) },
    { name: "Other fields", value: Math.round(stats.total_graduates_per_year - stats.ai_graduates_per_year) },
  ];

  return (
    <div className="bg-gray-900 rounded-2xl p-6">
      <h2 className="text-white font-semibold text-lg mb-1">Talent Supply</h2>
      <p className="text-gray-400 text-sm mb-4">Graduate output per year across all programs</p>

      <div className="flex items-center gap-6">
        <ResponsiveContainer width={140} height={140}>
          <PieChart>
            <Pie data={pieData} cx="50%" cy="50%" innerRadius={40} outerRadius={60} dataKey="value" strokeWidth={0}>
              {pieData.map((_, i) => <Cell key={i} fill={COLORS[i]} />)}
            </Pie>
            <Tooltip
              contentStyle={{ backgroundColor: "#1F2937", border: "none", borderRadius: 8 }}
              formatter={(v: unknown) => [(v as number).toLocaleString(), "graduates/yr"]}
            />
          </PieChart>
        </ResponsiveContainer>

        <div className="flex flex-col gap-3 flex-1">
          <Stat label="Total graduates/yr" value={stats.total_graduates_per_year.toLocaleString()} />
          <Stat label="AI-related graduates/yr" value={stats.ai_graduates_per_year.toLocaleString()} color="text-violet-400" />
          <Stat label="Avg income (AI fields, 5yr)" value={`$${stats.avg_income_5yr_ai.toLocaleString()}`} />
          <Stat label="AI-related programs" value={`${stats.ai_related_programs} / ${stats.total_programs}`} />
        </div>
      </div>
    </div>
  );
}

function Stat({ label, value, color = "text-white" }: { label: string; value: string; color?: string }) {
  return (
    <div>
      <p className="text-gray-400 text-xs">{label}</p>
      <p className={`font-semibold text-base ${color}`}>{value}</p>
    </div>
  );
}
