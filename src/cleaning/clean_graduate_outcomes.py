"""
Sprint 2 — Data Cleaning
Camada: processed_data
Dataset: Graduate Outcomes
Problema: inc_growth como string com %, colunas y1-y5 precisam de contexto
"""

import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_PATH = os.path.join(BASE_DIR, "data", "raw",
    "ae-labour-market-outcomes-graduates-publicly-funded-post-secondary-institutions-2024.csv")
OUT_PATH = os.path.join(BASE_DIR, "data", "processed", "graduate_outcomes_clean.csv")

# Palavras-chave para identificar campos de estudo relacionados a tecnologia/IA
# Usadas para criar um flag que facilita o filtro na análise do talent gap
AI_RELATED_KEYWORDS = [
    "computer", "software", "data", "information technology",
    "artificial intelligence", "machine learning", "network",
    "cybersecurity", "digital", "engineering technology",
]


def parse_inc_growth(value: str) -> float | None:
    """
    Converte a string de crescimento de renda para float.
    Ex: '24%' → 0.24 | '-5%' → -0.05 | 'N/A' → None
    """
    if pd.isna(value):
        return None
    cleaned = str(value).strip().replace("%", "").replace(",", "")
    try:
        return round(float(cleaned) / 100, 4)
    except ValueError:
        return None


def flag_ai_related(field: str) -> int:
    """
    Retorna 1 se o campo de estudo contém palavras relacionadas a IA/tech.
    Retorna 0 caso contrário.
    Usado para filtrar o supply de talentos relevante para o talent gap.
    """
    if pd.isna(field):
        return 0
    field_lower = str(field).lower()
    return int(any(kw in field_lower for kw in AI_RELATED_KEYWORDS))


def clean_graduate_outcomes() -> pd.DataFrame:
    """
    Pipeline de limpeza do dataset de resultados de graduados.
    """
    print("\n🔧 Limpando: Graduate Outcomes")

    df = pd.read_csv(RAW_PATH)
    print(f"  Carregado: {df.shape[0]} linhas")

    # Converte inc_growth de string para float decimal
    df["inc_growth"] = df["inc_growth"].apply(parse_inc_growth)

    # Renomeia colunas y1-y5 para nomes mais descritivos
    # y1 = renda no 1º ano após formatura, y5 = 5º ano
    df = df.rename(columns={
        "y1": "income_year1",
        "y2": "income_year2",
        "y3": "income_year3",
        "y4": "income_year4",
        "y5": "income_year5",
    })

    # Cria flag para campos de estudo relacionados a IA/tech
    df["is_ai_related"] = df["field_of_study_or_cip"].apply(flag_ai_related)

    # Calcula renda média ao longo dos 5 anos (proxy de estabilidade salarial)
    income_cols = ["income_year1", "income_year2", "income_year3",
                   "income_year4", "income_year5"]
    df["income_avg_5yr"] = df[income_cols].mean(axis=1).round(0)

    # Salva resultado
    df.to_csv(OUT_PATH, index=False)
    print(f"  ✅ Salvo em: {OUT_PATH}")

    return df


if __name__ == "__main__":
    df = clean_graduate_outcomes()
    print(df[["credential", "field_of_study_or_cip", "is_ai_related",
              "income_year1", "income_year5", "inc_growth", "income_avg_5yr"]].head(10).to_string(index=False))
