"""
Sprint 4 — API Layer
Camada: api_layer / routers
Responsabilidade: Endpoints relacionados a ocupações e talent gap.

Endpoints:
    GET /occupations              → lista todas as ocupações (paginado)
    GET /occupations/{noc_code}   → detalhe de uma ocupação
    GET /occupations/ai-adjacent  → apenas ocupações AI-adjacent
    GET /gaps                     → registros de talent gap (paginado + filtros)
    GET /gaps/summary             → resumo agregado por ocupação
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from src.api.dependencies import get_datasets, paginate
from src.api.models.schemas import (
    OccupationDetail, TalentGapRecord, PaginatedResponse
)

# APIRouter agrupa endpoints relacionados
# O prefixo e as tags aparecem automaticamente no Swagger UI
router = APIRouter(prefix="/occupations", tags=["Occupations & Talent Gap"])


@router.get(
    "/",
    response_model=PaginatedResponse,
    summary="List all occupations",
    description="Returns a paginated list of all 513 occupations with their attributes.",
)
def list_occupations(
    # Parâmetros de query com validação automática pelo Pydantic
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Records per page"),
    ai_adjacent_only: bool = Query(default=False, description="Filter AI-adjacent occupations only"),
    datasets=Depends(get_datasets),
):
    """
    Lista todas as ocupações com paginação.
    Parâmetro opcional ai_adjacent_only filtra apenas as 4 ocupações AI-adjacent.
    """
    df = datasets["dim_occupation"].copy()

    # Aplica filtro opcional
    if ai_adjacent_only:
        df = df[df["is_ai_adjacent"] == 1]

    # Substitui NaN por None para serialização JSON correta
    df = df.where(df.notna(), other=None)

    # Aplica paginação
    page_df, total = paginate(df, page, page_size)

    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        data=page_df.to_dict(orient="records"),
    )


@router.get(
    "/ai-adjacent",
    response_model=list[OccupationDetail],
    summary="List AI-adjacent occupations",
    description="Returns the 4 AI-adjacent occupations with full detail.",
)
def list_ai_adjacent(datasets=Depends(get_datasets)):
    """
    Retorna apenas as ocupações AI-adjacent com todos os atributos.
    Endpoint dedicado pois é o foco principal do projeto.
    """
    df = datasets["dim_occupation"]
    ai_df = df[df["is_ai_adjacent"] == 1].copy()

    # Ordena por demand/supply ratio (maior gap primeiro)
    ai_df = ai_df.sort_values("avg_demand_supply_ratio", ascending=False)
    ai_df = ai_df.where(ai_df.notna(), other=None)

    return ai_df.to_dict(orient="records")


@router.get(
    "/{noc_code}",
    response_model=OccupationDetail,
    summary="Get occupation by NOC code",
    description="Returns full detail for a single occupation identified by its 5-digit NOC code.",
)
def get_occupation(noc_code: str, datasets=Depends(get_datasets)):
    """
    Retorna os detalhes de uma ocupação específica pelo código NOC.
    Retorna 404 se o código não existir.
    """
    df = datasets["dim_occupation"]

    # Filtra pelo NOC code (comparação como string)
    result = df[df["noc_code"].astype(str) == str(noc_code)]

    if result.empty:
        # HTTPException com status 404 é o padrão REST para "não encontrado"
        raise HTTPException(
            status_code=404,
            detail=f"Occupation with NOC code '{noc_code}' not found."
        )

    row = result.iloc[0].where(result.iloc[0].notna(), other=None)
    return row.to_dict()


# ─────────────────────────────────────────────────────────────
# ENDPOINTS DE TALENT GAP
# Separados em prefixo próprio mas no mesmo router por coesão
# ─────────────────────────────────────────────────────────────

gap_router = APIRouter(prefix="/gaps", tags=["Talent Gap"])


@gap_router.get(
    "/",
    response_model=PaginatedResponse,
    summary="List talent gap records",
    description="Returns paginated talent gap records with optional filters by year, NOC code, or category.",
)
def list_gaps(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    year: int = Query(default=None, ge=2023, le=2033, description="Filter by projection year"),
    noc_code: str = Query(default=None, description="Filter by NOC code"),
    category: str = Query(default=None, description="Filter by gap category: Low, Moderate, Critical"),
    datasets=Depends(get_datasets),
):
    """
    Lista registros de talent gap com filtros opcionais.
    Combina dados da fact_talent_gap com nomes de ocupações.
    """
    fact = datasets["fact_talent_gap"].copy()
    dim_occ = datasets["dim_occupation"][["noc_code", "occupation"]]

    # Enriquece com nome da ocupação via merge
    fact = fact.merge(dim_occ, on="noc_code", how="left")

    # Aplica filtros opcionais
    if year is not None:
        fact = fact[fact["year"] == year]

    if noc_code is not None:
        fact = fact[fact["noc_code"].astype(str) == str(noc_code)]

    if category is not None:
        # Validação do valor do filtro
        valid_categories = ["Low", "Moderate", "Critical"]
        if category not in valid_categories:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid category '{category}'. Must be one of: {valid_categories}"
            )
        fact = fact[fact["gap_category"] == category]

    fact = fact.where(fact.notna(), other=None)
    page_df, total = paginate(fact, page, page_size)

    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        data=page_df.to_dict(orient="records"),
    )


@gap_router.get(
    "/summary",
    summary="Get talent gap summary by occupation",
    description="Returns aggregated gap metrics per occupation, sorted by average Talent Gap Index.",
)
def get_gap_summary(
    ai_adjacent_only: bool = Query(default=False),
    datasets=Depends(get_datasets),
):
    """
    Retorna um resumo agregado do talent gap por ocupação.
    Calcula médias ao longo dos 11 anos de projeção.
    Útil para rankings e visualizações de alto nível.
    """
    fact = datasets["fact_talent_gap"]
    dim_occ = datasets["dim_occupation"][["noc_code", "occupation", "is_ai_adjacent", "wage_median"]]

    # Agrega métricas por ocupação (média dos 11 anos)
    summary = fact.groupby("noc_code").agg(
        avg_talent_gap_index=("talent_gap_index", "mean"),
        avg_demand_supply_ratio=("demand_supply_ratio", "mean"),
        years_with_gap=("gap_flag", "sum"),
        avg_annual_openings=("net_change_job_openings", "mean"),
    ).reset_index()

    # Adiciona nome e atributos da ocupação
    summary = summary.merge(dim_occ, on="noc_code", how="left")

    # Filtra AI-adjacent se solicitado
    if ai_adjacent_only:
        summary = summary[summary["is_ai_adjacent"] == 1]

    # Ordena por gap index (maior primeiro)
    summary = summary.sort_values("avg_talent_gap_index", ascending=False)
    summary = summary.where(summary.notna(), other=None)

    return summary.to_dict(orient="records")


@gap_router.get(
    "/trend",
    summary="Get gap trend over time",
    description="Returns average Talent Gap Index per year (2023-2033) to show temporal trend.",
)
def get_gap_trend(
    noc_code: str = Query(default=None, description="Filter by NOC code for occupation-specific trend"),
    datasets=Depends(get_datasets),
):
    """
    Retorna a tendência temporal do gap ao longo dos 11 anos.
    Se noc_code for fornecido, retorna a tendência de uma ocupação específica.
    Caso contrário, retorna a média de todas as ocupações.
    """
    fact = datasets["fact_talent_gap"].copy()

    if noc_code is not None:
        fact = fact[fact["noc_code"].astype(str) == str(noc_code)]
        if fact.empty:
            raise HTTPException(status_code=404, detail=f"NOC code '{noc_code}' not found.")

    # Agrega por ano
    trend = fact.groupby("year").agg(
        avg_talent_gap_index=("talent_gap_index", "mean"),
        avg_demand_supply_ratio=("demand_supply_ratio", "mean"),
        total_openings=("net_change_job_openings", "sum"),
        total_seekers=("net_change_job_seekers", "sum"),
    ).reset_index()

    trend = trend.sort_values("year")
    trend = trend.where(trend.notna(), other=None)

    return trend.to_dict(orient="records")
