"use client";

import type { Occupation } from "@/lib/api";

const badge = (score?: number) => {
  if (!score) return null;
  const label = score >= 60 ? "Critical" : score >= 30 ? "Moderate" : "Low";
  const cls = score >= 60
    ? "bg-red-500/20 text-red-400"
    : score >= 30
    ? "bg-yellow-500/20 text-yellow-400"
    : "bg-green-500/20 text-green-400";
  return <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${cls}`}>{label}</span>;
};

export default function AiOccupationsTable({ data }: { data: Occupation[] }) {
  return (
    <div className="bg-gray-900 rounded-2xl p-6">
      <h2 className="text-white font-semibold text-lg mb-1">AI-Adjacent Occupations</h2>
      <p className="text-gray-400 text-sm mb-4">Detailed view of the 4 AI-adjacent occupations tracked</p>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-gray-400 border-b border-gray-800">
              <th className="text-left pb-2 font-medium">Occupation</th>
              <th className="text-right pb-2 font-medium">NOC</th>
              <th className="text-right pb-2 font-medium">Demand/Supply</th>
              <th className="text-right pb-2 font-medium">Wage (median)</th>
              <th className="text-right pb-2 font-medium">Yrs w/ Gap</th>
              <th className="text-right pb-2 font-medium">Outlook</th>
              <th className="pb-2" />
            </tr>
          </thead>
          <tbody>
            {data.map((occ) => (
              <tr key={occ.noc_code} className="border-b border-gray-800/50 hover:bg-gray-800/40 transition-colors">
                <td className="py-3 text-white font-medium">{occ.occupation}</td>
                <td className="py-3 text-right text-gray-400 font-mono">{occ.noc_code}</td>
                <td className="py-3 text-right text-violet-400 font-semibold">
                  {occ.avg_demand_supply_ratio?.toFixed(2) ?? "—"}x
                </td>
                <td className="py-3 text-right text-gray-300">
                  {occ.wage_median ? `$${occ.wage_median.toFixed(2)}/hr` : "—"}
                </td>
                <td className="py-3 text-right text-gray-300">{occ.years_with_gap ?? "—"} / 11</td>
                <td className="py-3 text-right text-gray-300">{occ.outlook_rating ?? "—"}</td>
                <td className="py-3 text-right">{badge(occ.avg_demand_supply_ratio ? occ.avg_demand_supply_ratio * 15 : undefined)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
