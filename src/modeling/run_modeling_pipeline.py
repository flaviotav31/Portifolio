"""
Sprint 3 — Pipeline de Modelagem
Camada: analytics_layer
Orquestra a construção de todas as tabelas do star schema.
Execute este arquivo para gerar a camada analytics completa.
"""

from build_dim_occupation import build_dim_occupation
from build_dim_time import build_dim_time
from build_dim_municipality import build_dim_municipality
from build_fact_talent_gap import build_fact_talent_gap
from build_supply_analysis import build_supply_analysis

if __name__ == "__main__":
    print("=" * 60)
    print("  Sprint 3 — Data Modeling Pipeline")
    print("=" * 60)
    
    # Constrói dimensões primeiro (fact depende delas)
    print("\n📐 FASE 1: Construindo Dimensões")
    dim_occ = build_dim_occupation()
    dim_time = build_dim_time()
    dim_muni = build_dim_municipality()
    
    # Constrói tabela fato
    print("\n📊 FASE 2: Construindo Tabela Fato")
    fact = build_fact_talent_gap()
    
    # Constrói tabelas analíticas adicionais
    print("\n🔬 FASE 3: Construindo Análises Complementares")
    supply = build_supply_analysis()
    
    # Relatório final
    print("\n" + "=" * 60)
    print("  ✅ Pipeline de Modelagem Concluído")
    print("=" * 60)
    print(f"\n  Dimensões:")
    print(f"    - dim_occupation:    {len(dim_occ):>6} linhas")
    print(f"    - dim_time:          {len(dim_time):>6} linhas")
    print(f"    - dim_municipality:  {len(dim_muni):>6} linhas")
    print(f"\n  Fatos:")
    print(f"    - fact_talent_gap:   {len(fact):>6} linhas")
    print(f"\n  Análises:")
    print(f"    - supply_analysis:   {len(supply):>6} linhas")
    
    # Insights rápidos
    print("\n" + "=" * 60)
    print("  📈 INSIGHTS RÁPIDOS")
    print("=" * 60)
    
    # Gap crítico
    critical_gaps = fact[fact["gap_category"] == "Critical"]
    print(f"\n  Registros com gap CRÍTICO: {len(critical_gaps)} ({len(critical_gaps)/len(fact)*100:.1f}%)")
    
    # Ocupações AI-adjacent
    ai_occ = dim_occ[dim_occ["is_ai_adjacent"] == 1]
    print(f"  Ocupações AI-adjacent: {len(ai_occ)} de {len(dim_occ)}")
    
    # Supply AI-related
    ai_supply = supply[supply["is_ai_related"] == 1]
    total_ai_grads = ai_supply["n_per_year"].sum()
    print(f"  Graduados/ano em campos AI: {total_ai_grads:.0f}")
    
    # Top 3 ocupações com maior gap médio
    top_gaps = (
        fact.groupby("noc_code")["talent_gap_index"]
        .mean()
        .sort_values(ascending=False)
        .head(3)
    )
    print(f"\n  Top 3 ocupações com maior Talent Gap Index médio:")
    for noc, score in top_gaps.items():
        occ_name = dim_occ[dim_occ["noc_code"] == noc]["occupation"].values[0]
        print(f"    - {noc} ({occ_name[:40]}...): {score:.1f}")
