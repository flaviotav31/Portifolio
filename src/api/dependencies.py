"""
Sprint 4 — API Layer
Camada: api_layer
Responsabilidade: Dependências compartilhadas entre todos os routers.

O padrão de "dependency injection" do FastAPI permite que funções
sejam injetadas nos endpoints via parâmetro. Aqui carregamos os
DataFrames uma única vez na inicialização da API (não a cada request).
"""

import pandas as pd
import numpy as np
from pathlib import Path
from functools import lru_cache

# Caminho base calculado a partir deste arquivo
BASE_DIR = Path(__file__).parent.parent.parent
ANALYTICS_DIR = BASE_DIR / "data" / "analytics"


@lru_cache(maxsize=None)
def load_datasets() -> dict[str, pd.DataFrame]:
    """
    Carrega todos os datasets da camada analytics em memória.

    @lru_cache garante que os dados são carregados apenas UMA VEZ,
    independente de quantas requests chegarem. Isso é essencial para
    performance — ler CSV a cada request seria inviável em produção.

    Retorna um dicionário com todos os DataFrames prontos para uso.
    """
    datasets = {
        "dim_occupation":   pd.read_csv(ANALYTICS_DIR / "dim_occupation.csv"),
        "dim_time":         pd.read_csv(ANALYTICS_DIR / "dim_time.csv"),
        "dim_municipality": pd.read_csv(ANALYTICS_DIR / "dim_municipality.csv"),
        "fact_talent_gap":  pd.read_csv(ANALYTICS_DIR / "fact_talent_gap.csv"),
        "supply_analysis":  pd.read_csv(ANALYTICS_DIR / "supply_analysis.csv"),
    }

    # Garante que noc_code é sempre string em todos os datasets
    for name in ("dim_occupation", "fact_talent_gap"):
        if "noc_code" in datasets[name].columns:
            datasets[name]["noc_code"] = datasets[name]["noc_code"].astype(str)

    # Substitui NaN/inf por None em todos os datasets de uma vez
    # JSON não aceita NaN — precisa ser null (None em Python)
    for name in datasets:
        datasets[name] = datasets[name].replace({np.nan: None, np.inf: None, -np.inf: None})

    return datasets


def get_datasets() -> dict[str, pd.DataFrame]:
    """
    Função de dependência injetada nos endpoints via FastAPI.

    Uso nos routers:
        @router.get("/")
        def list_items(datasets = Depends(get_datasets)):
            df = datasets["dim_occupation"]
    """
    return load_datasets()


def paginate(df: pd.DataFrame, page: int, page_size: int) -> tuple[pd.DataFrame, int]:
    """
    Aplica paginação a um DataFrame.

    Retorna uma tupla (página_atual, total_de_registros).
    Paginação é obrigatória em APIs públicas — retornar 169k registros
    de uma vez travaria o cliente e sobrecarregaria o servidor.
    """
    # Garante que page começa em 1
    page = max(1, page)
    page_size = min(100, max(1, page_size))  # limita entre 1 e 100

    total = len(df)
    start = (page - 1) * page_size
    end = start + page_size

    return df.iloc[start:end], total
