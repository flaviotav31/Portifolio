"""
Sprint 4 — API Layer
Camada: api_layer / routers
Responsabilidade: Endpoints de supply de talentos (graduados).

Endpoints:
    GET /supply              → lista programas de graduação (paginado)
    GET /supply/ai-related   → apenas campos AI-related
    GET /supply/stats        → estatísticas agregadas de supply
"""

from fastapi import APIRouter, Depends, Query
from src.api.dependencies import get_datasets, paginate
from src.api.models.schemas import PaginatedResponse

router = APIRouter(prefix="/supply", tags=["Talent Supply"])


@router.get(
    "/",
    response_model=PaginatedResponse,
    summary="List graduate programs",
    description="Returns paginated list of graduate programs with income and attractiveness metrics.",
)
def list_supply(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    ai_related_only: bool = Query(default=False, description="Filter AI/tech related fields only"),
    credential: str = Query(default=None, description="Filter by credential type (Certificate, Diploma, Degree)"),
    datasets=Depends(get_datasets),
):
    """
    Lista programas de graduação com métricas de supply.
    Filtros opcionais por relevância AI e tipo de credencial.
    """
    df = datasets["supply_analysis"].copy()

    if ai_related_only:
        df = df[df["is_ai_related"] == 1]

    if credential is not None:
        # Filtro case-insensitive para facilitar uso pelo frontend
        df = df[df["credential"].str.lower() == credential.lower()]

    df = df.where(df.notna(), other=None)
    page_df, total = paginate(df, page, page_size)

    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        data=page_df.to_dict(orient="records"),
    )


@router.get(
    "/ai-related",
    summary="List AI-related graduate programs",
    description="Returns all AI/tech related graduate programs sorted by attractiveness score.",
)
def list_ai_related_supply(datasets=Depends(get_datasets)):
    """
    Retorna todos os programas de graduação relacionados a IA/tech.
    Ordenados por attractiveness_score (maior primeiro).
    """
    df = datasets["supply_analysis"]
    ai_df = df[df["is_ai_related"] == 1].copy()
    ai_df = ai_df.sort_values("attractiveness_score", ascending=False)
    ai_df = ai_df.where(ai_df.notna(), other=None)

    return ai_df.to_dict(orient="records")


@router.get(
    "/stats",
    summary="Get supply statistics",
    description="Returns aggregated statistics about talent supply: total graduates, average income, etc.",
)
def get_supply_stats(datasets=Depends(get_datasets)):
    """
    Retorna estatísticas agregadas do supply de talentos.
    Útil para o card de resumo no dashboard.
    """
    df = datasets["supply_analysis"]
    ai_df = df[df["is_ai_related"] == 1]

    return {
        "total_programs": int(len(df)),
        "ai_related_programs": int(len(ai_df)),
        "total_graduates_per_year": float(df["n_per_year"].sum()),
        "ai_graduates_per_year": float(ai_df["n_per_year"].sum()),
        "avg_income_5yr_all": round(float(df["income_avg_5yr"].mean()), 0),
        "avg_income_5yr_ai": round(float(ai_df["income_avg_5yr"].mean()), 0),
        "credentials": df["credential"].value_counts().to_dict(),
    }
