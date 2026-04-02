"""
Script de Validação do Pipeline
Verifica se todas as etapas foram executadas corretamente
e se os dados estão consistentes.
"""

import pandas as pd
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

def check_file_exists(path: str, description: str) -> bool:
    """Verifica se um arquivo existe."""
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"  ✅ {description}: {size:,} bytes")
        return True
    else:
        print(f"  ❌ {description}: AUSENTE")
        return False

def validate_pipeline():
    """Valida todas as etapas do pipeline."""
    print("\n" + "=" * 60)
    print("  VALIDAÇÃO DO PIPELINE")
    print("=" * 60)
    
    all_valid = True
    
    # ─────────────────────────────────────────────────────────────
    # 1. Dados Brutos
    # ─────────────────────────────────────────────────────────────
    print("\n1. DADOS BRUTOS (raw/)")
    raw_files = [
        "ai_adjacent_profiles_final.csv",
        "jet-albertas-occupational-outlook-data-tables-2023-2033.xlsx",
        "ae-labour-market-outcomes-graduates-publicly-funded-post-secondary-institutions-2024.csv",
        "Businesses by municipality.csv",
        "Census employment by municipality.csv",
    ]
    
    for filename in raw_files:
        path = BASE_DIR / "data" / "raw" / filename
        if not check_file_exists(path, filename):
            all_valid = False
    
    # ─────────────────────────────────────────────────────────────
    # 2. Dados Processados
    # ─────────────────────────────────────────────────────────────
    print("\n2. DADOS PROCESSADOS (processed/)")
    processed_files = [
        "ai_profiles_clean.csv",
        "occupational_outlook_clean.csv",
        "graduate_outcomes_clean.csv",
        "businesses_clean.csv",
        "census_employment_clean.csv",
    ]
    
    for filename in processed_files:
        path = BASE_DIR / "data" / "processed" / filename
        if not check_file_exists(path, filename):
            all_valid = False
    
    # ─────────────────────────────────────────────────────────────
    # 3. Camada Analytics
    # ─────────────────────────────────────────────────────────────
    print("\n3. CAMADA ANALYTICS (analytics/)")
    analytics_files = [
        "dim_occupation.csv",
        "dim_time.csv",
        "dim_municipality.csv",
        "fact_talent_gap.csv",
        "supply_analysis.csv",
    ]
    
    for filename in analytics_files:
        path = BASE_DIR / "data" / "analytics" / filename
        if not check_file_exists(path, filename):
            all_valid = False
    
    # ─────────────────────────────────────────────────────────────
    # 4. Validação de Integridade dos Dados
    # ─────────────────────────────────────────────────────────────
    print("\n4. INTEGRIDADE DOS DADOS")
    
    try:
        # Carrega tabelas principais
        dim_occ = pd.read_csv(BASE_DIR / "data" / "analytics" / "dim_occupation.csv")
        dim_time = pd.read_csv(BASE_DIR / "data" / "analytics" / "dim_time.csv")
        fact = pd.read_csv(BASE_DIR / "data" / "analytics" / "fact_talent_gap.csv")
        supply = pd.read_csv(BASE_DIR / "data" / "analytics" / "supply_analysis.csv")
        
        # Valida contagens
        print(f"  ✅ dim_occupation: {len(dim_occ)} registros")
        print(f"  ✅ dim_time: {len(dim_time)} registros")
        print(f"  ✅ fact_talent_gap: {len(fact)} registros")
        print(f"  ✅ supply_analysis: {len(supply)} registros")
        
        # Valida integridade referencial
        fact_nocs = set(fact["noc_code"].unique())
        dim_nocs = set(dim_occ["noc_code"].unique())
        
        if fact_nocs.issubset(dim_nocs):
            print(f"  ✅ Integridade referencial: todos os NOCs do fact existem em dim_occupation")
        else:
            print(f"  ❌ Integridade referencial: NOCs órfãos no fact")
            all_valid = False
        
        # Valida métricas calculadas
        if "talent_gap_index" in fact.columns:
            print(f"  ✅ Talent Gap Index calculado")
            print(f"     - Mínimo: {fact['talent_gap_index'].min():.1f}")
            print(f"     - Máximo: {fact['talent_gap_index'].max():.1f}")
            print(f"     - Média: {fact['talent_gap_index'].mean():.1f}")
        else:
            print(f"  ❌ Talent Gap Index ausente")
            all_valid = False
        
        # Valida categorias
        categories = fact["gap_category"].value_counts()
        print(f"  ✅ Distribuição de gaps:")
        for cat, count in categories.items():
            pct = (count / len(fact)) * 100
            print(f"     - {cat}: {count} ({pct:.1f}%)")
        
    except Exception as e:
        print(f"  ❌ Erro ao validar integridade: {e}")
        all_valid = False
    
    # ─────────────────────────────────────────────────────────────
    # 5. Outputs
    # ─────────────────────────────────────────────────────────────
    print("\n5. OUTPUTS")
    report_path = BASE_DIR / "outputs" / "insights_report.txt"
    if check_file_exists(report_path, "insights_report.txt"):
        # Conta linhas do relatório
        with open(report_path, "r", encoding="utf-8") as f:
            lines = len(f.readlines())
        print(f"     Relatório tem {lines} linhas")
    else:
        all_valid = False
    
    # ─────────────────────────────────────────────────────────────
    # Resultado Final
    # ─────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    if all_valid:
        print("  ✅ PIPELINE VÁLIDO — Todos os componentes OK")
    else:
        print("  ❌ PIPELINE INCOMPLETO — Execute os scripts faltantes")
    print("=" * 60 + "\n")
    
    return all_valid

if __name__ == "__main__":
    validate_pipeline()
