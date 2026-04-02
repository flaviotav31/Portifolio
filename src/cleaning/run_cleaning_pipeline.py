"""
Sprint 2 — Pipeline de Limpeza
Camada: processed_data
Orquestra todos os scripts de limpeza em sequência.
Execute este arquivo para processar todos os datasets de uma vez.
"""

from clean_occupational_outlook import clean_occupational_outlook
from clean_ai_profiles import clean_ai_profiles
from clean_graduate_outcomes import clean_graduate_outcomes
from clean_municipal_data import clean_businesses, clean_census_employment

if __name__ == "__main__":
    print("=" * 60)
    print("  Sprint 2 — Data Cleaning Pipeline")
    print("=" * 60)

    results = {}

    # Executa cada limpeza e armazena o resultado
    results["occupational_outlook"] = clean_occupational_outlook()
    results["ai_profiles"]          = clean_ai_profiles()
    results["graduate_outcomes"]    = clean_graduate_outcomes()
    results["businesses"]           = clean_businesses()
    results["census_employment"]    = clean_census_employment()

    # Relatório final
    print("\n" + "=" * 60)
    print("  ✅ Pipeline concluído")
    print("=" * 60)
    for name, df in results.items():
        print(f"  {name}: {df.shape[0]} linhas x {df.shape[1]} colunas")
