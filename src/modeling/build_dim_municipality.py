"""
Sprint 3 — Data Modeling
Camada: analytics_layer
Dimensão: dim_municipality
Combina dados de Census + Businesses para criar perfil municipal.
"""

import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROCESSED = os.path.join(BASE_DIR, "data", "processed")
ANALYTICS = os.path.join(BASE_DIR, "data", "analytics")

os.makedirs(ANALYTICS, exist_ok=True)


def build_dim_municipality() -> pd.DataFrame:
    """
    Cria dimensão de municípios com métricas agregadas:
    - Total de empresas (média dos anos disponíveis)
    - Taxa de participação no mercado de trabalho (mais recente)
    - População economicamente ativa (proxy via census)
    """
    print("\n🔨 Construindo: dim_municipality")
    
    # Carrega dados limpos
    businesses = pd.read_csv(os.path.join(PROCESSED, "businesses_clean.csv"))
    census = pd.read_csv(os.path.join(PROCESSED, "census_employment_clean.csv"))
    
    # Extrai municípios únicos (usa businesses como base)
    dim = businesses[["csduid", "csd"]].drop_duplicates().copy()
    print(f"  Municípios únicos: {len(dim)}")
    
    # Agrega total de empresas por município (média ao longo dos anos)
    biz_agg = businesses.groupby("csduid").agg({
        "business_count": "sum",  # soma de todas as categorias/anos
    }).reset_index()
    
    biz_agg = biz_agg.rename(columns={"business_count": "total_businesses"})
    
    # Filtra dados de participação no mercado de trabalho do census
    # (indicador mais relevante para análise de talent gap)
    participation = census[
        census["indicatorsummarydescription"] == "participation rate"
    ].copy()
    
    # Pega o ano mais recente disponível por município
    participation = (
        participation
        .sort_values("period", ascending=False)
        .groupby("csduid")
        .first()
        .reset_index()
    )
    
    participation = participation[["csduid", "metric_value", "period"]]
    participation = participation.rename(columns={
        "metric_value": "labour_participation_rate",
        "period": "participation_rate_year",
    })
    
    # Combina tudo na dimensão
    dim = dim.merge(biz_agg, on="csduid", how="left")
    dim = dim.merge(participation, on="csduid", how="left")
    
    # Preenche nulos com 0 (municípios sem dados)
    dim["total_businesses"] = dim["total_businesses"].fillna(0).astype(int)
    dim["labour_participation_rate"] = dim["labour_participation_rate"].fillna(0)
    
    # Cria flag para municípios com dados completos
    dim["has_complete_data"] = (
        (dim["total_businesses"] > 0) & 
        (dim["labour_participation_rate"] > 0)
    ).astype(int)
    
    # Ordena por número de empresas (proxy de tamanho econômico)
    dim = dim.sort_values("total_businesses", ascending=False)
    
    # Adiciona ID sequencial
    dim.insert(0, "municipality_id", range(1, len(dim) + 1))
    
    # Salva
    out_path = os.path.join(ANALYTICS, "dim_municipality.csv")
    dim.to_csv(out_path, index=False)
    print(f"  ✅ {len(dim)} municípios → {out_path}")
    
    return dim


if __name__ == "__main__":
    dim = build_dim_municipality()
    
    # Mostra os top 10 municípios por atividade econômica
    print("\n  Top 10 municípios por total de empresas:")
    print(dim[[
        "csd", "total_businesses", "labour_participation_rate", "has_complete_data"
    ]].head(10).to_string(index=False))
