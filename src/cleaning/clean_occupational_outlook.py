"""
Sprint 2 — Data Cleaning
Camada: processed_data
Dataset: Occupational Outlook (Excel)
Problema: cabeçalho mal estruturado, colunas unnamed, linhas de separador
"""

import pandas as pd
import os

# Caminhos baseados na localização deste arquivo
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_PATH  = os.path.join(BASE_DIR, "data", "raw", "jet-albertas-occupational-outlook-data-tables-2023-2033.xlsx")
OUT_PATH  = os.path.join(BASE_DIR, "data", "processed", "occupational_outlook_clean.csv")

# Anos projetados pelo relatório (colunas 1 a 11 do Excel)
YEARS = list(range(2023, 2034))

# As 4 métricas que se repetem para cada ocupação no Excel
METRICS = [
    "net_change_job_openings",
    "net_change_job_seekers",
    "annual_imbalance",
    "cumulative_imbalance",
]


def load_raw_excel() -> pd.DataFrame:
    """
    Carrega o Excel sem nenhum header automático (header=None).
    Isso nos dá controle total sobre como interpretar cada linha.
    """
    # header=None → pandas não tenta adivinhar o cabeçalho
    df = pd.read_excel(RAW_PATH, sheet_name="Data", header=None)
    print(f"  Excel carregado: {df.shape[0]} linhas x {df.shape[1]} colunas")
    return df


def parse_occupation_blocks(df: pd.DataFrame) -> list[dict]:
    """
    O Excel tem uma estrutura em blocos:
      - Linha com NOC code + nome da ocupação (ex: '00011 Senior government...')
      - 4 linhas seguintes com as métricas (openings, seekers, imbalance, cumulative)

    Esta função percorre o DataFrame linha a linha,
    detecta os cabeçalhos de ocupação e extrai os valores das 4 métricas
    para cada um dos 11 anos (2023–2033).

    Retorna uma lista de dicionários, um por ocupação/ano.
    """
    records = []

    # Variável de estado: guarda a ocupação atual enquanto lemos suas métricas
    current_occupation = None
    current_noc        = None
    metric_index       = 0  # contador de 0 a 3 para saber qual métrica estamos lendo

    for _, row in df.iterrows():
        cell = str(row[0]).strip() if pd.notna(row[0]) else ""

        # Detecta linha de cabeçalho de ocupação:
        # Começa com código NOC (5 dígitos) seguido do nome
        # Ex: "00011 Senior government managers and officials"
        if len(cell) >= 5 and cell[:5].isdigit():
            # Salva o código NOC com zero-padding para garantir 5 dígitos
            # Ex: '11' lido como int vira '00011' após zfill(5)
            current_noc        = cell[:5].zfill(5)
            current_occupation = cell[6:].strip()  # remove o código do início
            metric_index       = 0                 # reinicia contador de métricas
            continue

        # Detecta linha de métrica: a coluna 1 (índice 1) tem o nome da métrica
        metric_label = str(row[1]).strip() if pd.notna(row[1]) else ""

        # Só processa se estamos dentro de uma ocupação e a linha tem métrica conhecida
        if current_occupation and metric_index < len(METRICS):
            metric_name = METRICS[metric_index]

            # Extrai os valores anuais (colunas 1 a 11 = anos 2023 a 2033)
            for i, year in enumerate(YEARS):
                value = row[i + 1]  # +1 porque coluna 0 é o nome da ocupação

                # Converte para float, usa None se não for número
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    value = None

                records.append({
                    "noc_code":   current_noc,
                    "occupation": current_occupation,
                    "year":       year,
                    "metric":     metric_name,
                    "value":      value,
                })

            metric_index += 1  # avança para a próxima métrica

    return records


def pivot_to_wide(records: list[dict]) -> pd.DataFrame:
    """
    Converte o formato longo (uma linha por ocupação/ano/métrica)
    para formato largo (uma linha por ocupação/ano, colunas = métricas).

    Formato longo → mais fácil de processar
    Formato largo → mais fácil de analisar e visualizar
    """
    df_long = pd.DataFrame(records)

    # pivot_table: cada combinação noc/occupation/year vira uma linha
    # cada valor de 'metric' vira uma coluna
    df_wide = df_long.pivot_table(
        index=["noc_code", "occupation", "year"],
        columns="metric",
        values="value",
        aggfunc="first",  # não há duplicatas, mas pivot_table exige aggfunc
    ).reset_index()

    # Remove o nome do índice de coluna criado pelo pivot
    df_wide.columns.name = None

    # Garante que as colunas de métricas existam mesmo se ausentes
    for m in METRICS:
        if m not in df_wide.columns:
            df_wide[m] = None

    # Reordena colunas de forma lógica
    df_wide = df_wide[["noc_code", "occupation", "year"] + METRICS]

    return df_wide


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria features derivadas úteis para análise do talent gap:

    - demand_supply_ratio: razão entre abertura de vagas e candidatos disponíveis
      > 1.0 = mais vagas que candidatos → pressão de demanda (talent gap)
      < 1.0 = mais candidatos que vagas → excesso de oferta

    - gap_flag: flag binária indicando se há gap de talento naquele ano
    """
    # Evita divisão por zero substituindo 0 por NaN temporariamente
    seekers = df["net_change_job_seekers"].replace(0, float("nan"))

    # Razão demanda/oferta: quanto maior, maior o gap
    df["demand_supply_ratio"] = (
        df["net_change_job_openings"] / seekers
    ).round(4)

    # Flag: 1 se há mais vagas que candidatos, 0 caso contrário
    df["gap_flag"] = (
        df["net_change_job_openings"] > df["net_change_job_seekers"]
    ).astype(int)

    return df


def clean_occupational_outlook() -> pd.DataFrame:
    """
    Pipeline completo de limpeza do Occupational Outlook.
    Orquestra todas as etapas e salva o resultado em processed/.
    """
    print("\n🔧 Limpando: Occupational Outlook")

    # Etapa 1: carrega o Excel bruto
    df_raw = load_raw_excel()

    # Etapa 2: extrai os blocos de ocupação em formato estruturado
    records = parse_occupation_blocks(df_raw)
    print(f"  Registros extraídos: {len(records)}")

    # Etapa 3: converte para formato largo (uma linha por ocupação/ano)
    df = pivot_to_wide(records)
    print(f"  Após pivot: {df.shape[0]} linhas x {df.shape[1]} colunas")

    # Etapa 4: remove linhas onde todos os valores de métricas são nulos
    df = df.dropna(subset=METRICS, how="all")
    print(f"  Após remover nulos: {df.shape[0]} linhas")

    # Etapa 5: adiciona features analíticas
    df = add_features(df)

    # Etapa 6: salva em processed/
    df.to_csv(OUT_PATH, index=False)
    print(f"  ✅ Salvo em: {OUT_PATH}")

    return df


if __name__ == "__main__":
    df = clean_occupational_outlook()
    print(f"\n  Amostra:")
    print(df.head(5).to_string(index=False))
