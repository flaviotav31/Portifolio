"""
Teste funcional da API — Sprint 4
Roda todos os endpoints e verifica respostas sem precisar subir o servidor.
"""

import sys
sys.path.insert(0, ".")

from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def run_tests():
    print("\n" + "=" * 60)
    print("  TESTE DE ENDPOINTS — AI Talent Gap API")
    print("=" * 60)

    # Define os testes: (descrição, response, status_codes_esperados)
    tests = [
        ("GET /",                                  client.get("/"),                                              [200]),
        ("GET /health",                            client.get("/health"),                                        [200]),
        ("GET /api/v1/occupations",                client.get("/api/v1/occupations"),                           [200]),
        ("GET /api/v1/occupations?ai_adjacent_only=true", client.get("/api/v1/occupations?ai_adjacent_only=true"), [200]),
        ("GET /api/v1/occupations/ai-adjacent",   client.get("/api/v1/occupations/ai-adjacent"),               [200]),
        ("GET /api/v1/occupations/21231",          client.get("/api/v1/occupations/21231"),                     [200]),
        ("GET /api/v1/occupations/99999 (404)",    client.get("/api/v1/occupations/99999"),                     [404]),
        ("GET /api/v1/gaps",                       client.get("/api/v1/gaps"),                                  [200]),
        ("GET /api/v1/gaps?year=2023",             client.get("/api/v1/gaps?year=2023"),                        [200]),
        ("GET /api/v1/gaps?category=Critical",     client.get("/api/v1/gaps?category=Critical"),                [200]),
        ("GET /api/v1/gaps?category=Invalid (422)",client.get("/api/v1/gaps?category=Invalid"),                 [422]),
        ("GET /api/v1/gaps/summary",               client.get("/api/v1/gaps/summary"),                         [200]),
        ("GET /api/v1/gaps/summary?ai_adjacent_only=true", client.get("/api/v1/gaps/summary?ai_adjacent_only=true"), [200]),
        ("GET /api/v1/gaps/trend",                 client.get("/api/v1/gaps/trend"),                           [200]),
        ("GET /api/v1/gaps/trend?noc_code=21231",  client.get("/api/v1/gaps/trend?noc_code=21231"),            [200]),
        ("GET /api/v1/supply",                     client.get("/api/v1/supply"),                               [200]),
        ("GET /api/v1/supply/ai-related",          client.get("/api/v1/supply/ai-related"),                    [200]),
        ("GET /api/v1/supply/stats",               client.get("/api/v1/supply/stats"),                         [200]),
        ("GET /api/v1/municipalities",             client.get("/api/v1/municipalities"),                       [200]),
        ("GET /api/v1/municipalities/top",         client.get("/api/v1/municipalities/top?n=5"),               [200]),
        ("GET /api/v1/municipalities/4811061",     client.get("/api/v1/municipalities/4811061"),               [200, 404]),
    ]

    passed = 0
    failed = 0

    print()
    for name, response, expected in tests:
        ok = response.status_code in expected
        icon = "✅" if ok else "❌"
        if ok:
            passed += 1
        else:
            failed += 1
        print(f"  {icon} {name:<50} → HTTP {response.status_code}")

    print(f"\n  Resultado: {passed} passou, {failed} falhou\n")

    # ── Amostra de dados reais ────────────────────────────────
    print("=" * 60)
    print("  AMOSTRA DE DADOS REAIS")
    print("=" * 60)

    # AI-adjacent occupations
    r = client.get("/api/v1/occupations/ai-adjacent")
    data = r.json()
    print(f"\n  AI-adjacent occupations ({len(data)} total):")
    for occ in data:
        ratio = occ.get("avg_demand_supply_ratio") or 0
        wage = occ.get("wage_median") or 0
        print(f"    {occ['noc_code']} | {occ['occupation'][:40]:<40} | ratio: {ratio:.2f} | ${wage:.2f}/hr")

    # Gap trend
    r2 = client.get("/api/v1/gaps/trend")
    trend = r2.json()
    print(f"\n  Gap trend (avg Talent Gap Index por ano):")
    for row in trend:
        bar = "█" * int(row["avg_talent_gap_index"] / 3)
        print(f"    {int(row['year'])} | {bar} {row['avg_talent_gap_index']:.1f}")

    # Supply stats
    r3 = client.get("/api/v1/supply/stats")
    stats = r3.json()
    print(f"\n  Supply stats:")
    for k, v in stats.items():
        if not isinstance(v, dict):
            print(f"    {k}: {v}")

    # Security headers
    r4 = client.get("/")
    print(f"\n  Security headers presentes:")
    security_headers = [
        "x-frame-options",
        "x-content-type-options",
        "strict-transport-security",
        "referrer-policy",
    ]
    for h in security_headers:
        val = r4.headers.get(h, "AUSENTE")
        icon = "✅" if val != "AUSENTE" else "❌"
        print(f"    {icon} {h}: {val}")

    print()
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
