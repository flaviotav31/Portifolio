"""
Sprint 3 — Relatório de Insights
Camada: analytics_layer
Gera um relatório executivo conectando demand (fact_talent_gap)
com supply (supply_analysis) para identificar os maiores gaps.
"""

import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ANALYTICS = os.path.join(BASE_DIR, "data", "analytics")
OUTPUTS = os.path.join(BASE_DIR, "outputs")

os.makedirs(OUTPUTS, exist_ok=True)


def generate_insights_report():
    """
    Gera relatório executivo com os principais insights do talent gap.
    """
    print("\n📊 Gerando Relatório de Insights")
    
    # Carrega dados analytics
    fact = pd.read_csv(os.path.join(ANALYTICS, "fact_talent_gap.csv"))
    dim_occ = pd.read_csv(os.path.join(ANALYTICS, "dim_occupation.csv"))
    supply = pd.read_csv(os.path.join(ANALYTICS, "supply_analysis.csv"))
    
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("  AI TALENT GAP IN ALBERTA — EXECUTIVE INSIGHTS REPORT")
    report_lines.append("=" * 80)
    report_lines.append("")
    
    # ─────────────────────────────────────────────────────────────
    # INSIGHT 1: Ocupações com maior gap crítico
    # ─────────────────────────────────────────────────────────────
    report_lines.append("1. OCUPAÇÕES COM MAIOR TALENT GAP (2023-2033)")
    report_lines.append("-" * 80)
    
    # Calcula gap médio por ocupação ao longo dos 11 anos
    gap_by_occ = (
        fact.groupby("noc_code")
        .agg({
            "talent_gap_index": "mean",
            "demand_supply_ratio": "mean",
            "net_change_job_openings": "mean",
        })
        .reset_index()
        .sort_values("talent_gap_index", ascending=False)
    )
    
    # Adiciona nome da ocupação
    gap_by_occ = gap_by_occ.merge(
        dim_occ[["noc_code", "occupation", "is_ai_adjacent"]],
        on="noc_code"
    )
    
    # Top 10 gaps
    top_gaps = gap_by_occ.head(10)
    report_lines.append("")
    report_lines.append("Top 10 ocupações com maior Talent Gap Index médio:")
    report_lines.append("")
    
    for i, row in top_gaps.iterrows():
        ai_flag = "🤖 AI-ADJACENT" if row["is_ai_adjacent"] == 1 else ""
        report_lines.append(
            f"  {row['noc_code']} | {row['occupation'][:50]:<50} | "
            f"Gap: {row['talent_gap_index']:>5.1f} | "
            f"D/S: {row['demand_supply_ratio']:>4.2f} {ai_flag}"
        )
    
    report_lines.append("")
    
    # ─────────────────────────────────────────────────────────────
    # INSIGHT 2: AI-Adjacent ocupações — análise específica
    # ─────────────────────────────────────────────────────────────
    report_lines.append("")
    report_lines.append("2. ANÁLISE DE OCUPAÇÕES AI-ADJACENT")
    report_lines.append("-" * 80)
    
    ai_occupations = dim_occ[dim_occ["is_ai_adjacent"] == 1].copy()
    ai_occupations = ai_occupations.sort_values("avg_demand_supply_ratio", ascending=False)
    
    report_lines.append("")
    for _, row in ai_occupations.iterrows():
        report_lines.append(f"\n  📌 {row['occupation']}")
        report_lines.append(f"     NOC: {row['noc_code']}")
        report_lines.append(f"     Demand/Supply Ratio: {row['avg_demand_supply_ratio']:.2f}")
        report_lines.append(f"     Anos com gap: {row['years_with_gap']:.0f} de 11")
        report_lines.append(f"     Salário mediano: ${row['wage_median']:.2f}/hora")
        report_lines.append(f"     Vagas anuais (média): {row['avg_annual_openings']:.0f}")
    
    report_lines.append("")
    
    # ─────────────────────────────────────────────────────────────
    # INSIGHT 3: Supply de talentos AI-related
    # ─────────────────────────────────────────────────────────────
    report_lines.append("")
    report_lines.append("3. SUPPLY DE TALENTOS EM CAMPOS AI-RELATED")
    report_lines.append("-" * 80)
    
    ai_supply = supply[supply["is_ai_related"] == 1].copy()
    total_ai_grads = ai_supply["n_per_year"].sum()
    avg_income = ai_supply["income_avg_5yr"].mean()
    
    report_lines.append("")
    report_lines.append(f"  Total de graduados/ano em campos AI: {total_ai_grads:.0f}")
    report_lines.append(f"  Renda média (5 anos): ${avg_income:,.0f}")
    report_lines.append("")
    report_lines.append("  Top 5 programas por volume de graduados:")
    report_lines.append("")
    
    top_supply = ai_supply.nlargest(5, "n_per_year")
    for _, row in top_supply.iterrows():
        report_lines.append(
            f"    • {row['field_of_study_or_cip'][:60]:<60} | "
            f"{row['n_per_year']:>3.0f}/ano | "
            f"${row['income_avg_5yr']:>6,.0f}"
        )
    
    report_lines.append("")
    
    # ─────────────────────────────────────────────────────────────
    # INSIGHT 4: Gap entre demand e supply
    # ─────────────────────────────────────────────────────────────
    report_lines.append("")
    report_lines.append("4. ANÁLISE DEMAND vs SUPPLY")
    report_lines.append("-" * 80)
    
    # Calcula demanda total de AI-adjacent ocupações
    ai_nocs = ai_occupations["noc_code"].tolist()
    ai_demand = fact[fact["noc_code"].isin(ai_nocs)]
    avg_annual_demand = ai_demand["net_change_job_openings"].mean()
    
    report_lines.append("")
    report_lines.append(f"  Demanda anual média (AI-adjacent): {avg_annual_demand:.0f} vagas")
    report_lines.append(f"  Supply anual (AI-related grads):   {total_ai_grads:.0f} graduados")
    report_lines.append("")
    
    gap_ratio = avg_annual_demand / total_ai_grads if total_ai_grads > 0 else 0
    
    if gap_ratio > 1:
        report_lines.append(f"  ⚠️  GAP IDENTIFICADO: Demanda é {gap_ratio:.1f}x maior que supply")
        report_lines.append(f"      Déficit estimado: ~{avg_annual_demand - total_ai_grads:.0f} talentos/ano")
    else:
        report_lines.append(f"  ✅ Supply atende demanda (ratio: {gap_ratio:.2f})")
    
    report_lines.append("")
    
    # ─────────────────────────────────────────────────────────────
    # INSIGHT 5: Tendência temporal
    # ─────────────────────────────────────────────────────────────
    report_lines.append("")
    report_lines.append("5. TENDÊNCIA TEMPORAL DO GAP (2023-2033)")
    report_lines.append("-" * 80)
    
    # Calcula gap médio por ano
    gap_by_year = (
        fact.groupby("year")["talent_gap_index"]
        .mean()
        .reset_index()
    )
    
    report_lines.append("")
    report_lines.append("  Talent Gap Index médio por ano:")
    report_lines.append("")
    
    for _, row in gap_by_year.iterrows():
        bar_length = int(row["talent_gap_index"] / 2)
        bar = "█" * bar_length
        report_lines.append(f"    {row['year']} | {bar} {row['talent_gap_index']:.1f}")
    
    # Calcula tendência
    first_year = gap_by_year.iloc[0]["talent_gap_index"]
    last_year = gap_by_year.iloc[-1]["talent_gap_index"]
    trend = ((last_year - first_year) / first_year) * 100
    
    report_lines.append("")
    if trend > 0:
        report_lines.append(f"  📈 Tendência: CRESCENTE (+{trend:.1f}% de 2023 a 2033)")
    else:
        report_lines.append(f"  📉 Tendência: DECRESCENTE ({trend:.1f}% de 2023 a 2033)")
    
    report_lines.append("")
    report_lines.append("=" * 80)
    
    # Salva relatório
    report_text = "\n".join(report_lines)
    report_path = os.path.join(OUTPUTS, "insights_report.txt")
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    
    print(f"  ✅ Relatório salvo em: {report_path}")
    print("\n" + report_text)
    
    return report_text


if __name__ == "__main__":
    generate_insights_report()
