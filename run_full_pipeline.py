"""
Entry point do projeto AI Talent Gap in Alberta.
Executa o pipeline completo: Raw → Processed → Analytics → Insights.

Execute a partir da raiz do projeto:
    py run_full_pipeline.py
"""

import sys
import traceback

# Imports usando package paths (src/ é um package via __init__.py)
from src.ingestion.load_raw_data import run_ingestion
from src.cleaning.clean_occupational_outlook import clean_occupational_outlook
from src.cleaning.clean_ai_profiles import clean_ai_profiles
from src.cleaning.clean_graduate_outcomes import clean_graduate_outcomes
from src.cleaning.clean_municipal_data import clean_businesses, clean_census_employment
from src.modeling.build_dim_occupation import build_dim_occupation
from src.modeling.build_dim_time import build_dim_time
from src.modeling.build_dim_municipality import build_dim_municipality
from src.modeling.build_fact_talent_gap import build_fact_talent_gap
from src.modeling.build_supply_analysis import build_supply_analysis
from src.modeling.generate_insights_report import generate_insights_report
from validate_pipeline import validate_pipeline


def run_full_pipeline():
    """
    Orquestra todas as etapas do pipeline de dados.
    Chama cada módulo em ordem e reporta o progresso.
    """
    print("\n" + "=" * 70)
    print("  AI TALENT GAP IN ALBERTA — FULL PIPELINE")
    print("=" * 70)

    try:
        # ── Sprint 1: Ingestão ────────────────────────────────────────────
        print("\n── SPRINT 1 — DATA INGESTION " + "─" * 41)
        datasets = run_ingestion()
        print(f"\n  ✅ {len(datasets)} datasets carregados")

        # ── Sprint 2: Limpeza ─────────────────────────────────────────────
        print("\n── SPRINT 2 — DATA CLEANING " + "─" * 42)
        clean_occupational_outlook()
        clean_ai_profiles()
        clean_graduate_outcomes()
        clean_businesses()
        clean_census_employment()
        print("\n  ✅ 5 datasets limpos")

        # ── Sprint 3: Modelagem ───────────────────────────────────────────
        print("\n── SPRINT 3 — DATA MODELING " + "─" * 42)
        build_dim_occupation()
        build_dim_time()
        build_dim_municipality()
        build_fact_talent_gap()
        build_supply_analysis()
        print("\n  ✅ Star schema criado")

        # ── Insights ──────────────────────────────────────────────────────
        print("\n── INSIGHTS REPORT " + "─" * 50)
        generate_insights_report()

        # ── Validação ─────────────────────────────────────────────────────
        print("\n── VALIDATION " + "─" * 55)
        is_valid = validate_pipeline()

        if is_valid:
            print("\n" + "=" * 70)
            print("  🎉 PIPELINE CONCLUÍDO COM SUCESSO!")
            print("=" * 70)
        else:
            print("\n  ⚠️  Pipeline executado com avisos. Revisar logs acima.")

    except Exception as e:
        print(f"\n  ❌ ERRO: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_full_pipeline()
