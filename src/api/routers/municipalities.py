"""
Sprint 4 — API Layer
Camada: api_layer / routers
Responsabilidade: Endpoints de dados municipais.

Endpoints:
    GET /municipalities          → lista municípios (paginado)
    GET /municipalities/{csduid} → detalhe de um município
    GET /municipalities/top      → top N municípios por atividade econômica
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from src.api.dependencies import get_datasets, paginate
from src.api.models.schemas import PaginatedResponse

router = APIRouter(prefix="/municipalities", tags=["Municipalities"])


@router.get(
    "/",
    response_model=PaginatedResponse,
    summary="List municipalities",
    description="Returns paginated list of Alberta municipalities with economic indicators.",
)
def list_municipalities(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    has_complete_data: bool = Query(default=False, description="Filter municipalities with complete data only"),
    datasets=Depends(get_datasets),
):
    df = datasets["dim_municipality"].copy()

    if has_complete_data:
        df = df[df["has_complete_data"] == 1]

    df = df.where(df.notna(), other=None)
    page_df, total = paginate(df, page, page_size)

    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        data=page_df.to_dict(orient="records"),
    )


@router.get(
    "/top",
    summary="Get top municipalities by economic activity",
    description="Returns the top N municipalities ranked by total business count.",
)
def get_top_municipalities(
    n: int = Query(default=10, ge=1, le=50, description="Number of municipalities to return"),
    datasets=Depends(get_datasets),
):
    """
    Retorna os N municípios com maior atividade econômica.
    Proxy de onde estão concentradas as oportunidades de emprego.
    """
    df = datasets["dim_municipality"].copy()
    top = df.nlargest(n, "total_businesses")
    top = top.where(top.notna(), other=None)

    return top.to_dict(orient="records")


@router.get(
    "/{csduid}",
    summary="Get municipality by CSD UID",
    description="Returns full detail for a single municipality identified by its CSD UID.",
)
def get_municipality(csduid: int, datasets=Depends(get_datasets)):
    """
    Retorna os detalhes de um município específico pelo CSD UID.
    CSD = Census Subdivision — identificador único de Statistics Canada.
    """
    df = datasets["dim_municipality"]
    result = df[df["csduid"] == csduid]

    if result.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Municipality with CSD UID '{csduid}' not found."
        )

    row = result.iloc[0].where(result.iloc[0].notna(), other=None)
    return row.to_dict()
