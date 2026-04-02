"""
Sprint 1 — Data Ingestion
Camada: raw_data
Responsabilidade: Carregar, inspecionar e validar os arquivos brutos do projeto.
"""

import pandas as pd
import os

# ─────────────────────────────────────────────
# CONFIGURAÇÃO DE CAMINHOS
# ─────────────────────────────────────────────

# Caminho base calculado a partir da localização deste arquivo
# Isso garante que o script funcione independente de onde é executado
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Caminho base para os dados brutos
RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw")

# Caminho de destino para dados processados (próxima camada)
PROCESSED_DATA_PATH = os.path.join(BASE_DIR, "data", "processed")

# Mapeamento dos arquivos disponíveis com nomes padronizados
# Chave: nome interno do dataset | Valor: nome do arquivo original
RAW_FILES = {
    "ai_profiles":       "ai_adjacent_profiles_final.csv",
    "occupational_outlook": "jet-albertas-occupational-outlook-data-tables-2023-2033.xlsx",
    "graduate_outcomes": "ae-labour-market-outcomes-graduates-publicly-funded-post-secondary-institutions-2024.csv",
    "businesses":        "Businesses by municipality.csv",
    "census_employment": "Census employment by municipality.csv",
}


# ─────────────────────────────────────────────
# FUNÇÕES AUXILIARES
# ─────────────────────────────────────────────

def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Padroniza os nomes das colunas de um DataFrame:
    - Converte para minúsculas
    - Substitui espaços por underscores
    - Remove caracteres especiais comuns
    Isso evita erros de referência por diferença de capitalização.
    """
    df.columns = (
        df.columns
        .str.strip()           # remove espaços nas bordas
        .str.lower()           # tudo minúsculo
        .str.replace(" ", "_", regex=False)   # espaços → underscore
        .str.replace(r"[^\w]", "_", regex=True)  # caracteres especiais → underscore
    )
    return df


def validate_dataframe(name: str, df: pd.DataFrame) -> None:
    """
    Executa validações básicas de integridade em um DataFrame:
    - Verifica se está vazio
    - Conta valores nulos por coluna
    - Exibe tipos de dados
    Essencial para detectar problemas antes de qualquer transformação.
    """
    print(f"\n{'='*60}")
    print(f"  Dataset: {name.upper()}")
    print(f"{'='*60}")
    print(f"  Linhas:   {df.shape[0]}")
    print(f"  Colunas:  {df.shape[1]}")

    # Alerta se o DataFrame estiver vazio
    if df.empty:
        print("  ⚠️  AVISO: DataFrame está vazio!")
        return

    # Conta nulos por coluna e exibe apenas as que têm nulos
    null_counts = df.isnull().sum()
    cols_with_nulls = null_counts[null_counts > 0]

    if cols_with_nulls.empty:
        print("  ✅ Sem valores nulos detectados.")
    else:
        print(f"\n  ⚠️  Colunas com valores nulos:")
        for col, count in cols_with_nulls.items():
            pct = (count / len(df)) * 100
            print(f"     - {col}: {count} nulos ({pct:.1f}%)")

    # Exibe os tipos de dados de cada coluna
    print(f"\n  Tipos de dados:")
    for col, dtype in df.dtypes.items():
        print(f"     - {col}: {dtype}")

    # Exibe as primeiras 2 linhas para inspeção visual rápida
    print(f"\n  Amostra (2 linhas):")
    print(df.head(2).to_string(index=False))


# ─────────────────────────────────────────────
# FUNÇÕES DE CARREGAMENTO
# ─────────────────────────────────────────────

def load_csv(name: str, filename: str) -> pd.DataFrame:
    """
    Carrega um arquivo CSV do diretório raw.
    Tenta diferentes encodings para evitar erros com caracteres especiais.
    Retorna um DataFrame com colunas padronizadas.
    """
    filepath = os.path.join(RAW_DATA_PATH, filename)

    # Tenta UTF-8 primeiro (padrão moderno), depois latin-1 (comum em dados canadenses)
    for encoding in ["utf-8", "latin-1", "cp1252"]:
        try:
            df = pd.read_csv(filepath, encoding=encoding)
            print(f"  ✅ [{name}] carregado com encoding '{encoding}'")
            return standardize_columns(df)
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            print(f"  ❌ [{name}] Arquivo não encontrado: {filepath}")
            return pd.DataFrame()

    print(f"  ❌ [{name}] Falha ao decodificar o arquivo.")
    return pd.DataFrame()


def load_excel(name: str, filename: str) -> dict[str, pd.DataFrame]:
    """
    Carrega um arquivo Excel com múltiplas abas.
    Retorna um dicionário onde cada chave é o nome da aba
    e o valor é o DataFrame correspondente com colunas padronizadas.
    """
    filepath = os.path.join(RAW_DATA_PATH, filename)

    try:
        # Carrega todas as abas do Excel de uma vez
        excel_data = pd.read_excel(filepath, sheet_name=None)
        sheets = {}
        for sheet_name, df in excel_data.items():
            # Padroniza o nome da aba também
            clean_name = sheet_name.strip().lower().replace(" ", "_")
            sheets[clean_name] = standardize_columns(df)
            print(f"  ✅ [{name}] Aba '{sheet_name}' carregada → '{clean_name}'")
        return sheets
    except FileNotFoundError:
        print(f"  ❌ [{name}] Arquivo não encontrado: {filepath}")
        return {}


# ─────────────────────────────────────────────
# FUNÇÃO PRINCIPAL
# ─────────────────────────────────────────────

def run_ingestion() -> dict:
    """
    Orquestra o carregamento de todos os datasets do projeto.
    Retorna um dicionário com todos os DataFrames carregados,
    prontos para validação e uso nas próximas etapas.
    """
    print("\n🚀 Iniciando Sprint 1 — Data Ingestion")
    print(f"   Fonte: {RAW_DATA_PATH}\n")

    datasets = {}

    # ── Carrega CSVs ──────────────────────────────────────
    csv_files = {k: v for k, v in RAW_FILES.items() if v.endswith(".csv")}
    for name, filename in csv_files.items():
        df = load_csv(name, filename)
        if not df.empty:
            datasets[name] = df

    # ── Carrega Excel (múltiplas abas) ────────────────────
    excel_files = {k: v for k, v in RAW_FILES.items() if v.endswith(".xlsx")}
    for name, filename in excel_files.items():
        sheets = load_excel(name, filename)
        # Cada aba vira um dataset separado com prefixo do nome original
        for sheet_name, df in sheets.items():
            key = f"{name}__{sheet_name}"
            datasets[key] = df

    # ── Validação de todos os datasets ───────────────────
    print("\n\n📋 RELATÓRIO DE VALIDAÇÃO")
    for name, df in datasets.items():
        validate_dataframe(name, df)

    print(f"\n\n✅ Ingestão concluída. {len(datasets)} datasets carregados.")
    return datasets


# ─────────────────────────────────────────────
# PONTO DE ENTRADA
# ─────────────────────────────────────────────

if __name__ == "__main__":
    # Executa a ingestão quando o script é chamado diretamente
    all_datasets = run_ingestion()
