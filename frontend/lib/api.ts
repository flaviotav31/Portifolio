const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { next: { revalidate: 3600 } });
  if (!res.ok) throw new Error(`API error ${res.status}: ${path}`);
  return res.json();
}

// ── Types ────────────────────────────────────────────────────

export interface Occupation {
  noc_code: string;
  occupation: string;
  is_ai_adjacent: number;
  outlook_rating?: string;
  outlook_score?: number;
  wage_low?: number;
  wage_median?: number;
  wage_high?: number;
  avg_annual_openings?: number;
  avg_annual_seekers?: number;
  avg_demand_supply_ratio?: number;
  years_with_gap?: number;
  education_required?: string;
  experience_required?: string;
}

export interface GapTrend {
  year: number;
  avg_talent_gap_index: number;
  avg_demand_supply_ratio: number;
  total_openings: number;
  total_seekers: number;
}

export interface GapSummary {
  noc_code: string;
  occupation: string;
  is_ai_adjacent: number;
  avg_talent_gap_index: number;
  avg_demand_supply_ratio: number;
  years_with_gap: number;
  avg_annual_openings: number;
  wage_median?: number;
}

export interface SupplyStats {
  total_programs: number;
  ai_related_programs: number;
  total_graduates_per_year: number;
  ai_graduates_per_year: number;
  avg_income_5yr_all: number;
  avg_income_5yr_ai: number;
  credentials: Record<string, number>;
}

export interface Municipality {
  municipality_id: number;
  csduid: number;
  csd: string;
  total_businesses: number;
  labour_participation_rate?: number;
  has_complete_data: number;
}

// ── API calls ────────────────────────────────────────────────

export const api = {
  aiOccupations: () => get<Occupation[]>("/api/v1/occupations/ai-adjacent"),
  gapTrend: (noc_code?: string) =>
    get<GapTrend[]>(`/api/v1/gaps/trend${noc_code ? `?noc_code=${noc_code}` : ""}`),
  gapSummary: () => get<GapSummary[]>("/api/v1/gaps/summary?ai_adjacent_only=true"),
  supplyStats: () => get<SupplyStats>("/api/v1/supply/stats"),
  topMunicipalities: (n = 10) => get<Municipality[]>(`/api/v1/municipalities/top?n=${n}`),
};
