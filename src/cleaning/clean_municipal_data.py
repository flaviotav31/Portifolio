"""
Sprint 2 — Data Cleaning
Camada: processed_data
Datasets: Businesses by Municipality + Census Employment
Problema: coluna unitofmeasure 100% nula, naics com tipos mistos
"""

import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RAW_BIZ   = os.path.join(BASE_DIR, "data", "raw", "Businesses by municipality.csv")
RAW_CEN   = os.path.join(BASE_DIR, "data", "raw", "Census employment by municipality.csv")
OUT_BIZ   = os.path.join(BASE_DIR, "data", "processed", "businesses_clean.csv")
OUT_CEN   = os.path.join(BASE_DIR, "data", "processed", "census_employment_clean.csv")


def clean_businesses() -> pd.DataFrame:
    """
    Limpa o dataset de empresas por município.
    Remove coluna nula, corrige tipo do NAICS, filtra anos relevantes.
    """
    print("\n🔧 Limpando: Businesses by Municipality")

    # low_memory=False evita o DtypeWarning da coluna naics com tipos mistos
    df = pd.read_csv(RAW_BIZ, low_memory=False)
    print(f"  Carregado: {df.shape[0]} linhas")

    # Padroniza nomes de colunas
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_", regex=False)

    # Remove coluna 100% nula — não agrega nenhuma informação
    df = df.drop(columns=["unitofmeasure"], errors="ignore")

    # Converte naics para string para evitar comparações inconsistentes
    # (alguns valores são int, outros são string no arquivo original)
    df["naics"] = df["naics"].astype(str).str.strip()

    # Remove linhas sem valor (originalvalue nulo = dado ausente)
    df = df.dropna(subset=["originalvalue"])

    # Converte originalvalue para inteiro (número de empresas é sempre inteiro)
    df["originalvalue"] = df["originalvalue"].astype(int)

    # Renomeia para nome mais descritivo
    df = df.rename(columns={"originalvalue": "business_count"})

    df.to_csv(OUT_BIZ, index=False)
    print(f"  ✅ Salvo: {df.shape[0]} linhas → {OUT_BIZ}")
    return df


def clean_census_employment() -> pd.DataFrame:
    """
    Limpa o dataset de emprego por município (Census).
    Remove coluna nula, padroniza indicadores, filtra dados relevantes.
    """
    print("\n🔧 Limpando: Census Employment by Municipality")

    df = pd.read_csv(RAW_CEN, low_memory=False)
    print(f"  Carregado: {df.shape[0]} linhas")

    # Padroniza nomes de colunas
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_", regex=False)

    # Remove coluna 100% nula
    df = df.drop(columns=["unitofmeasure"], errors="ignore")

    # Remove linhas sem valor
    df = df.dropna(subset=["originalvalue"])

    # Renomeia para nome mais descritivo
    df = df.rename(columns={"originalvalue": "metric_value"})

    # Padroniza o campo de indicador para minúsculas (facilita filtros futuros)
    df["indicatorsummarydescription"] = (
        df["indicatorsummarydescription"].str.strip().str.lower()
    )

    df.to_csv(OUT_CEN, index=False)
    print(f"  ✅ Salvo: {df.shape[0]} linhas → {OUT_CEN}")
    return df


if __name__ == "__main__":
    df_biz = clean_businesses()
    print(f"\n  Amostra businesses:")
    print(df_biz.head(3).to_string(index=False))

    df_cen = clean_census_employment()
    print(f"\n  Amostra census:")
    print(df_cen.head(3).to_string(index=False))
