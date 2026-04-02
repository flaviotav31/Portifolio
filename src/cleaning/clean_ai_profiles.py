"""
Sprint 2 — Data Cleaning
Camada: processed_data
Dataset: AI Adjacent Profiles
Problema: salários em string única, outlook_rating como texto
"""

import pandas as pd
import re
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_PATH = os.path.join(BASE_DIR, "data", "raw", "ai_adjacent_profiles_final.csv")
OUT_PATH = os.path.join(BASE_DIR, "data", "processed", "ai_profiles_clean.csv")

# Mapeamento de outlook textual para score numérico
# Permite ordenar e comparar ocupações quantitativamente
OUTLOOK_SCORE_MAP = {
    "above average": 3,
    "hot":           3,   # ALIS usa "Hot" para demanda muito alta
    "average":       2,
    "warm":          2,
    "balanced":      2,
    "below average": 1,
    "cool":          1,
    "cold":          1,
    "limited":       1,
}


def parse_wages(wage_str: str) -> tuple[float | None, float | None, float | None]:
    """
    Extrai os 3 valores de salário de uma string no formato:
    '$29.09 / $53.11 / $80.91'

    Retorna uma tupla (wage_low, wage_median, wage_high) como floats.
    Retorna (None, None, None) se o formato não for reconhecido.
    """
    if pd.isna(wage_str) or not isinstance(wage_str, str):
        return None, None, None

    # Extrai todos os números decimais da string (ignora $ e espaços)
    values = re.findall(r"\d+\.\d+", wage_str)

    if len(values) == 3:
        return float(values[0]), float(values[1]), float(values[2])

    # Caso tenha formato diferente, retorna None para investigação
    return None, None, None


def map_outlook_score(rating: str) -> int | None:
    """
    Converte o outlook textual (ex: 'Above Average') para um score numérico.
    Facilita ordenação e uso em modelos analíticos.
    """
    if pd.isna(rating):
        return None
    # Normaliza para minúsculas antes de buscar no mapa
    return OUTLOOK_SCORE_MAP.get(str(rating).strip().lower(), None)


def clean_ai_profiles() -> pd.DataFrame:
    """
    Pipeline de limpeza do dataset de perfis AI-adjacent.
    """
    print("\n🔧 Limpando: AI Adjacent Profiles")

    df = pd.read_csv(RAW_PATH)
    print(f"  Carregado: {df.shape[0]} linhas")

    # Padroniza nomes de colunas
    df.columns = (
        df.columns.str.strip().str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace(r"[^\w]", "_", regex=True)
    )

    # Renomeia a coluna de salário para nome mais curto antes de processar
    df = df.rename(columns={
        "wage_low___median___high__hourly_": "wage_raw",
        "outlook_rating": "outlook_rating",
    })

    # Separa a string de salário em 3 colunas numéricas
    wages = df["wage_raw"].apply(parse_wages)
    df["wage_low"]    = wages.apply(lambda x: x[0])
    df["wage_median"] = wages.apply(lambda x: x[1])
    df["wage_high"]   = wages.apply(lambda x: x[2])

    # Cria score numérico para o outlook
    df["outlook_score"] = df["outlook_rating"].apply(map_outlook_score)

    # Remove a coluna bruta de salário (já extraída)
    df = df.drop(columns=["wage_raw"])

    # Salva resultado
    df.to_csv(OUT_PATH, index=False)
    print(f"  ✅ Salvo em: {OUT_PATH}")
    print(f"  Colunas finais: {df.columns.tolist()}")

    return df


if __name__ == "__main__":
    df = clean_ai_profiles()
    print(df[["occupation", "outlook_rating", "outlook_score",
              "wage_low", "wage_median", "wage_high"]].to_string(index=False))
