"""
Sprint 3 — Data Modeling
Camada: analytics_layer
Dimensão: dim_time
Tabela simples de anos com atributos úteis para análise temporal.
"""

import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ANALYTICS = os.path.join(BASE_DIR, "data", "analytics")

os.makedirs(ANALYTICS, exist_ok=True)


def build_dim_time() -> pd.DataFrame:
    """
    Cria dimensão temporal para os anos de projeção (2023-2033).
    Adiciona atributos úteis para análise:
    - year_offset: anos desde o início da projeção (0 a 10)
    - period_label: rótulo descritivo (ex: "Short-term", "Mid-term", "Long-term")
    """
    print("\n🔨 Construindo: dim_time")
    
    years = list(range(2023, 2034))
    
    dim = pd.DataFrame({
        "year": years,
        "year_offset": range(0, 11),  # 0 = 2023, 10 = 2033
    })
    
    # Classifica os anos em períodos de análise
    # Útil para agregações e visualizações
    def classify_period(offset):
        if offset <= 2:
            return "Short-term (2023-2025)"
        elif offset <= 5:
            return "Mid-term (2026-2028)"
        else:
            return "Long-term (2029-2033)"
    
    dim["period_label"] = dim["year_offset"].apply(classify_period)
    
    # Adiciona ID sequencial
    dim.insert(0, "time_id", range(1, len(dim) + 1))
    
    # Salva
    out_path = os.path.join(ANALYTICS, "dim_time.csv")
    dim.to_csv(out_path, index=False)
    print(f"  ✅ {len(dim)} anos → {out_path}")
    
    return dim


if __name__ == "__main__":
    dim = build_dim_time()
    print(dim.to_string(index=False))
