"""
Sprint 3 — Data Modeling
Camada: analytics_layer
Tabela: supply_analysis
Analisa o supply de talentos (graduados) por área de estudo,
com foco em campos relacionados a IA/tech.
"""

import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROCESSED = os.path.join(BASE_DIR, "data", "processed")
ANALYTICS = os.path.join(BASE_DIR, "data", "analytics")

os.makedirs(ANALYTICS, exist_ok=True)


def build_supply_analysis() -> pd.DataFrame:
    """
    Cria tabela analítica do supply de talentos:
    - Graduados por credencial e campo de estudo
    - Renda média e crescimento
    - Flag de relevância para IA/tech
    - Estimativa de supply anual
    """
    print("\n🔨 Construindo: supply_analysis")
    
    # Carrega dados limpos
    graduates = pd.read_csv(os.path.join(PROCESSED, "graduate_outcomes_clean.csv"))
    
    # Cria tabela analítica
    supply = graduates.copy()
    
    # Adiciona ID sequencial
    supply.insert(0, "supply_id", range(1, len(supply) + 1))
    
    # Calcula score de atratividade da área de estudo
    # Combina: renda média + crescimento de renda + volume de graduados
    # Normaliza para 0-100
    
    # Normaliza renda média (0-50 pontos)
    income_max = supply["income_avg_5yr"].max()
    supply["income_score"] = (supply["income_avg_5yr"] / income_max * 50).fillna(0)
    
    # Normaliza crescimento de renda (0-30 pontos)
    # inc_growth já está em decimal (0.24 = 24%)
    supply["growth_score"] = (supply["inc_growth"] * 100).fillna(0).clip(0, 30)
    
    # Normaliza volume de graduados (0-20 pontos)
    volume_max = supply["n_per_year"].max()
    supply["volume_score"] = (supply["n_per_year"] / volume_max * 20).fillna(0)
    
    # Score total de atratividade
    supply["attractiveness_score"] = (
        supply["income_score"] + 
        supply["growth_score"] + 
        supply["volume_score"]
    ).round(2)
    
    # Classifica em categorias
    def classify_attractiveness(score):
        if pd.isna(score):
            return "Unknown"
        elif score < 40:
            return "Low"
        elif score < 70:
            return "Moderate"
        else:
            return "High"
    
    supply["attractiveness_category"] = supply["attractiveness_score"].apply(
        classify_attractiveness
    )
    
    # Ordena por relevância para IA e atratividade
    supply = supply.sort_values(
        ["is_ai_related", "attractiveness_score"],
        ascending=[False, False]
    )
    
    # Seleciona colunas finais
    supply = supply[[
        "supply_id",
        "credential",
        "field_of_study_or_cip",
        "is_ai_related",
        "n_per_year",
        "income_year1",
        "income_year5",
        "income_avg_5yr",
        "inc_diff",
        "inc_growth",
        "attractiveness_score",
        "attractiveness_category",
    ]]
    
    # Salva
    out_path = os.path.join(ANALYTICS, "supply_analysis.csv")
    supply.to_csv(out_path, index=False)
    print(f"  ✅ {len(supply)} programas → {out_path}")
    
    return supply


if __name__ == "__main__":
    supply = build_supply_analysis()
    
    # Mostra campos AI-related com maior atratividade
    print("\n  Top 10 campos AI-related por atratividade:")
    ai_fields = supply[supply["is_ai_related"] == 1]
    print(ai_fields[[
        "field_of_study_or_cip",
        "credential",
        "n_per_year",
        "income_avg_5yr",
        "attractiveness_score",
    ]].head(10).to_string(index=False))
    
    # Estatísticas gerais
    print(f"\n  Total de graduados/ano em campos AI-related: {ai_fields['n_per_year'].sum():.0f}")
    print(f"  Renda média 5yr (AI-related): ${ai_fields['income_avg_5yr'].mean():.0f}")
