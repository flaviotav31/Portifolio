"""
Sprint 3 — Data Modeling
Camada: analytics_layer
Dimensão: dim_occupation
Combina dados de AI Profiles + Occupational Outlook para criar
uma tabela mestre de ocupações com todos os atributos relevantes.
"""

import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROCESSED = os.path.join(BASE_DIR, "data", "processed")
ANALYTICS = os.path.join(BASE_DIR, "data", "analytics")

# Cria pasta analytics se não existir
os.makedirs(ANALYTICS, exist_ok=True)


def build_dim_occupation() -> pd.DataFrame:
    """
    Cria a dimensão de ocupações combinando:
    - AI Profiles (12 ocupações AI-adjacent com detalhes)
    - Occupational Outlook (513 ocupações com projeções)
    
    A dimensão final contém TODAS as ocupações do outlook,
    enriquecidas com dados de AI profiles quando disponível.
    """
    print("\n🔨 Construindo: dim_occupation")
    
    # Carrega dados limpos
    ai_profiles = pd.read_csv(os.path.join(PROCESSED, "ai_profiles_clean.csv"))
    outlook = pd.read_csv(os.path.join(PROCESSED, "occupational_outlook_clean.csv"))
    
    # Extrai ocupações únicas do outlook (base da dimensão)
    dim = outlook[["noc_code", "occupation"]].drop_duplicates().copy()
    print(f"  Ocupações únicas no outlook: {len(dim)}")
    
    # Normaliza nomes de ocupações para facilitar o join
    # (AI profiles tem capitalização diferente do outlook)
    dim["occupation_normalized"] = dim["occupation"].str.strip().str.lower()
    ai_profiles["occupation_normalized"] = ai_profiles["occupation"].str.strip().str.lower()
    
    # Faz left join: mantém todas as ocupações do outlook,
    # adiciona dados de AI profiles quando houver match
    dim = dim.merge(
        ai_profiles[[
            "occupation_normalized",
            "outlook_rating",
            "outlook_score", 
            "education_required",
            "experience_required",
            "wage_low",
            "wage_median",
            "wage_high",
            "brief_description",
        ]],
        on="occupation_normalized",
        how="left"
    )
    
    # Remove coluna auxiliar de normalização
    dim = dim.drop(columns=["occupation_normalized"])
    
    # Cria flag indicando se a ocupação é AI-adjacent
    # (tem dados detalhados no AI profiles)
    dim["is_ai_adjacent"] = dim["outlook_rating"].notna().astype(int)
    
    # Calcula métricas agregadas do outlook para cada ocupação
    # (média ao longo dos 11 anos de projeção)
    outlook_agg = outlook.groupby("noc_code").agg({
        "net_change_job_openings": "mean",
        "net_change_job_seekers": "mean",
        "demand_supply_ratio": "mean",
        "gap_flag": "sum",  # quantos anos têm gap
    }).reset_index()
    
    outlook_agg = outlook_agg.rename(columns={
        "net_change_job_openings": "avg_annual_openings",
        "net_change_job_seekers": "avg_annual_seekers",
        "demand_supply_ratio": "avg_demand_supply_ratio",
        "gap_flag": "years_with_gap",  # de 0 a 11
    })
    
    # Adiciona as métricas agregadas à dimensão
    dim = dim.merge(outlook_agg, on="noc_code", how="left")
    
    # Ordena por demanda (ocupações com maior gap primeiro)
    dim = dim.sort_values("avg_demand_supply_ratio", ascending=False)
    
    # Adiciona ID sequencial (chave primária da dimensão)
    dim.insert(0, "occupation_id", range(1, len(dim) + 1))
    
    # Salva
    out_path = os.path.join(ANALYTICS, "dim_occupation.csv")
    dim.to_csv(out_path, index=False)
    print(f"  ✅ {len(dim)} ocupações → {out_path}")
    
    return dim


if __name__ == "__main__":
    dim = build_dim_occupation()
    
    # Mostra as top 10 ocupações com maior gap
    print("\n  Top 10 ocupações com maior demand/supply ratio:")
    print(dim[[
        "noc_code", "occupation", "is_ai_adjacent",
        "avg_demand_supply_ratio", "years_with_gap"
    ]].head(10).to_string(index=False))
