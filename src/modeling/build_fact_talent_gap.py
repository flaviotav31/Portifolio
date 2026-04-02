"""
Sprint 3 — Data Modeling
Camada: analytics_layer
Fato: fact_talent_gap
Tabela central do star schema com métricas de talent gap
por ocupação/ano (granularidade temporal).
"""

import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROCESSED = os.path.join(BASE_DIR, "data", "processed")
ANALYTICS = os.path.join(BASE_DIR, "data", "analytics")

os.makedirs(ANALYTICS, exist_ok=True)


def calculate_talent_gap_index(row: pd.Series) -> float:
    """
    Calcula o AI Talent Gap Index — métrica composta que combina:
    
    1. Demand/Supply Ratio (peso 50%): quanto maior, maior o gap
    2. Cumulative Imbalance (peso 30%): acúmulo de gap ao longo do tempo
    3. Outlook Score (peso 20%): perspectiva de crescimento da ocupação
    
    Retorna um score de 0 a 100, onde:
    - 0-30: baixo gap (oferta atende demanda)
    - 31-60: gap moderado (pressão crescente)
    - 61-100: gap crítico (escassez severa de talentos)
    """
    # Componente 1: Demand/Supply Ratio normalizado
    # Valores típicos: 0.8 a 1.5 (1.0 = equilíbrio)
    # Normaliza para 0-50 (peso 50%)
    ratio = row.get("demand_supply_ratio", 1.0)
    if pd.isna(ratio) or ratio <= 0:
        ratio_score = 0
    else:
        # Quanto maior que 1.0, maior o score
        # 1.5+ = score máximo de 50
        ratio_score = min(50, (ratio - 0.8) * 100)
        ratio_score = max(0, ratio_score)
    
    # Componente 2: Cumulative Imbalance normalizado
    # Valores típicos: -5000 a +15000
    # Normaliza para 0-30 (peso 30%)
    cumulative = row.get("cumulative_imbalance", 0)
    if pd.isna(cumulative):
        cumulative_score = 0
    else:
        # Valores positivos = gap acumulado
        # 10000+ = score máximo de 30
        cumulative_score = min(30, (cumulative / 10000) * 30)
        cumulative_score = max(0, cumulative_score)
    
    # Componente 3: Outlook Score
    # Valores: 1, 2, 3 (já normalizado)
    # Normaliza para 0-20 (peso 20%)
    outlook = row.get("outlook_score", 2)
    if pd.isna(outlook):
        outlook_score = 10  # valor neutro
    else:
        # 1 → 0, 2 → 10, 3 → 20
        outlook_score = (outlook - 1) * 10
    
    # Soma ponderada
    total_score = ratio_score + cumulative_score + outlook_score
    
    return round(total_score, 2)


def build_fact_talent_gap() -> pd.DataFrame:
    """
    Constrói a tabela fato combinando:
    - Occupational Outlook (métricas temporais)
    - dim_occupation (IDs e atributos)
    - dim_time (IDs temporais)
    
    Adiciona o AI Talent Gap Index calculado.
    """
    print("\n🔨 Construindo: fact_talent_gap")
    
    # Carrega dados
    outlook = pd.read_csv(os.path.join(PROCESSED, "occupational_outlook_clean.csv"))
    dim_occ = pd.read_csv(os.path.join(ANALYTICS, "dim_occupation.csv"))
    dim_time = pd.read_csv(os.path.join(ANALYTICS, "dim_time.csv"))
    
    # Cria a base da tabela fato a partir do outlook
    fact = outlook.copy()
    
    # Adiciona occupation_id via join com dim_occupation
    fact = fact.merge(
        dim_occ[["noc_code", "occupation_id", "outlook_score"]],
        on="noc_code",
        how="left"
    )
    
    # Adiciona time_id via join com dim_time
    fact = fact.merge(
        dim_time[["year", "time_id"]],
        on="year",
        how="left"
    )
    
    # Calcula o AI Talent Gap Index para cada linha
    print("  Calculando AI Talent Gap Index...")
    fact["talent_gap_index"] = fact.apply(calculate_talent_gap_index, axis=1)
    
    # Classifica o gap em categorias para facilitar análise
    def classify_gap(score):
        if pd.isna(score):
            return "Unknown"
        elif score < 30:
            return "Low"
        elif score < 60:
            return "Moderate"
        else:
            return "Critical"
    
    fact["gap_category"] = fact["talent_gap_index"].apply(classify_gap)
    
    # Seleciona e ordena colunas finais
    fact = fact[[
        "occupation_id",
        "time_id",
        "noc_code",
        "year",
        "net_change_job_openings",
        "net_change_job_seekers",
        "annual_imbalance",
        "cumulative_imbalance",
        "demand_supply_ratio",
        "gap_flag",
        "talent_gap_index",
        "gap_category",
    ]]
    
    # Ordena por gap index (maiores gaps primeiro)
    fact = fact.sort_values(["talent_gap_index", "year"], ascending=[False, True])
    
    # Adiciona ID sequencial (chave primária da tabela fato)
    fact.insert(0, "fact_id", range(1, len(fact) + 1))
    
    # Salva
    out_path = os.path.join(ANALYTICS, "fact_talent_gap.csv")
    fact.to_csv(out_path, index=False)
    print(f"  ✅ {len(fact)} registros → {out_path}")
    
    return fact


if __name__ == "__main__":
    fact = build_fact_talent_gap()
    
    # Mostra distribuição de gaps por categoria
    print("\n  Distribuição de gaps por categoria:")
    print(fact["gap_category"].value_counts().to_string())
    
    # Mostra top 10 registros com maior gap
    print("\n  Top 10 registros com maior Talent Gap Index:")
    print(fact[[
        "noc_code", "year", "talent_gap_index", "gap_category",
        "demand_supply_ratio", "cumulative_imbalance"
    ]].head(10).to_string(index=False))
