import { api } from "@/lib/api";
import GapTrendChart from "@/components/GapTrendChart";
import OccupationRanking from "@/components/OccupationRanking";
import SupplyDemandCard from "@/components/SupplyDemandCard";
import AiOccupationsTable from "@/components/AiOccupationsTable";
import StatCard from "@/components/StatCard";
import { TrendingUp, Users, Briefcase, AlertTriangle } from "lucide-react";

export const revalidate = 3600;

export default async function DashboardPage() {
  const [occupations, trend, summary, supplyStats] = await Promise.all([
    api.aiOccupations(),
    api.gapTrend(),
    api.gapSummary(),
    api.supplyStats(),
  ]);

  const topGap = summary[0];
  const criticalCount = summary.filter((s) => s.avg_talent_gap_index >= 60).length;

  return (
    <main className="min-h-screen bg-gray-950 text-white">
      {/* Header */}
      <div className="border-b border-gray-800 px-6 py-5">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-white">AI Talent Gap — Alberta</h1>
            <p className="text-gray-400 text-sm mt-0.5">Occupational demand vs supply analysis · 2023–2033</p>
          </div>
          <a
            href="/"
            className="text-sm text-violet-400 hover:text-violet-300 transition-colors"
          >
            ← Back to portfolio
          </a>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8 space-y-6">
        {/* KPI cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            label="Highest Gap Index"
            value={topGap?.avg_talent_gap_index.toFixed(1) ?? "—"}
            sub={topGap?.occupation}
            icon={AlertTriangle}
            accent="text-red-400"
          />
          <StatCard
            label="Critical Occupations"
            value={`${criticalCount} / ${summary.length}`}
            sub="Gap Index > 60"
            icon={TrendingUp}
            accent="text-orange-400"
          />
          <StatCard
            label="AI Graduates / yr"
            value={Math.round(supplyStats.ai_graduates_per_year).toLocaleString()}
            sub={`of ${Math.round(supplyStats.total_graduates_per_year).toLocaleString()} total`}
            icon={Users}
            accent="text-violet-400"
          />
          <StatCard
            label="Avg Income (AI, 5yr)"
            value={`$${supplyStats.avg_income_5yr_ai.toLocaleString()}`}
            sub="CAD · median"
            icon={Briefcase}
            accent="text-emerald-400"
          />
        </div>

        {/* Charts row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <GapTrendChart data={trend} />
          <SupplyDemandCard stats={supplyStats} />
        </div>

        {/* Ranking */}
        <OccupationRanking data={summary} />

        {/* Table */}
        <AiOccupationsTable data={occupations} />

        {/* Footer note */}
        <p className="text-center text-gray-600 text-xs pb-4">
          Data source: Alberta Occupational Outlook 2023–2033 · Graduate Outcomes 2024 · Statistics Canada
        </p>
      </div>
    </main>
  );
}
