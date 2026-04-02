"use client";

import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine,
} from "recharts";
import type { GapTrend } from "@/lib/api";

export default function GapTrendChart({ data }: { data: GapTrend[] }) {
  return (
    <div className="bg-gray-900 rounded-2xl p-6">
      <h2 className="text-white font-semibold text-lg mb-1">Talent Gap Index — Trend (2023–2033)</h2>
      <p className="text-gray-400 text-sm mb-4">Average gap index across all AI-adjacent occupations per year</p>
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={data} margin={{ top: 4, right: 16, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis dataKey="year" stroke="#9CA3AF" tick={{ fontSize: 12 }} />
          <YAxis stroke="#9CA3AF" tick={{ fontSize: 12 }} domain={[0, 100]} />
          <Tooltip
            contentStyle={{ backgroundColor: "#1F2937", border: "none", borderRadius: 8 }}
            labelStyle={{ color: "#F9FAFB" }}
            itemStyle={{ color: "#A78BFA" }}
            formatter={(v: unknown) => [(v as number).toFixed(1), "Gap Index"]}
          />
          <ReferenceLine y={60} stroke="#EF4444" strokeDasharray="4 4" label={{ value: "Critical", fill: "#EF4444", fontSize: 11, position: "insideTopRight" }} />
          <ReferenceLine y={30} stroke="#F59E0B" strokeDasharray="4 4" label={{ value: "Moderate", fill: "#F59E0B", fontSize: 11, position: "insideBottomRight" }} />
          <Line
            type="monotone"
            dataKey="avg_talent_gap_index"
            stroke="#A78BFA"
            strokeWidth={2.5}
            dot={{ fill: "#A78BFA", r: 4 }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
