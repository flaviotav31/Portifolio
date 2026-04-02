"""
Sprint 4 — API Layer
Camada: api_layer / models
Responsabilidade: Definir os schemas de resposta da API usando Pydantic.

Pydantic valida automaticamente os dados antes de retorná-los ao cliente.
Se um campo estiver faltando ou com tipo errado, a API retorna erro 422
em vez de dados corrompidos — isso é segurança por design.
"""

from pydantic import BaseModel, Field
from typing import Optional


# ─────────────────────────────────────────────────────────────
# SCHEMAS DE OCUPAÇÃO
# ─────────────────────────────────────────────────────────────

class OccupationBase(BaseModel):
    """
    Schema base de uma ocupação.
    Campos presentes em todas as respostas relacionadas a ocupações.
    """
    # Código NOC: identificador único canadense de 5 dígitos
    noc_code: str = Field(..., description="National Occupational Classification code (5 digits)")
    occupation: str = Field(..., description="Occupation name")
    is_ai_adjacent: int = Field(..., description="1 if AI-adjacent occupation, 0 otherwise")


class OccupationDetail(OccupationBase):
    """
    Schema completo de uma ocupação com todos os atributos.
    Retornado no endpoint GET /occupations/{noc_code}.
    """
    # Atributos de mercado de trabalho
    outlook_rating: Optional[str] = Field(None, description="Qualitative outlook (e.g. 'Above Average')")
    outlook_score: Optional[float] = Field(None, description="Numeric outlook score (1-3)")
    education_required: Optional[str] = None
    experience_required: Optional[str] = None

    # Salários por hora (em dólares canadenses)
    wage_low: Optional[float] = Field(None, description="Low hourly wage (CAD)")
    wage_median: Optional[float] = Field(None, description="Median hourly wage (CAD)")
    wage_high: Optional[float] = Field(None, description="High hourly wage (CAD)")

    # Métricas agregadas (média dos 11 anos de projeção)
    avg_annual_openings: Optional[float] = Field(None, description="Average annual job openings (2023-2033)")
    avg_annual_seekers: Optional[float] = Field(None, description="Average annual job seekers (2023-2033)")
    avg_demand_supply_ratio: Optional[float] = Field(None, description="Average demand/supply ratio")
    years_with_gap: Optional[float] = Field(None, description="Number of years (out of 11) with talent gap")

    # Permite que o Pydantic leia campos de objetos (ex: pandas Series)
    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────
# SCHEMAS DE TALENT GAP
# ─────────────────────────────────────────────────────────────

class TalentGapRecord(BaseModel):
    """
    Schema de um registro da tabela fato.
    Representa o gap de uma ocupação em um ano específico.
    """
    noc_code: str
    year: int
    net_change_job_openings: Optional[float] = Field(None, description="Projected job openings")
    net_change_job_seekers: Optional[float] = Field(None, description="Projected job seekers")
    annual_imbalance: Optional[float] = Field(None, description="Openings minus seekers")
    cumulative_imbalance: Optional[float] = Field(None, description="Accumulated imbalance over time")
    demand_supply_ratio: Optional[float] = Field(None, description="Ratio of openings to seekers")
    gap_flag: Optional[int] = Field(None, description="1 if gap exists this year, 0 otherwise")
    talent_gap_index: Optional[float] = Field(None, description="Composite gap score (0-100)")
    gap_category: Optional[str] = Field(None, description="Low / Moderate / Critical")

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────
# SCHEMAS DE SUPPLY (GRADUADOS)
# ─────────────────────────────────────────────────────────────

class SupplyRecord(BaseModel):
    """
    Schema de um programa de graduação com métricas de supply.
    """
    credential: str = Field(..., description="Type of credential (Certificate, Diploma, Degree)")
    field_of_study_or_cip: str = Field(..., description="Field of study name")
    is_ai_related: int = Field(..., description="1 if AI/tech related field, 0 otherwise")
    n_per_year: Optional[float] = Field(None, description="Average graduates per year")
    income_year1: Optional[float] = Field(None, description="Median income in year 1 after graduation (CAD)")
    income_year5: Optional[float] = Field(None, description="Median income in year 5 after graduation (CAD)")
    income_avg_5yr: Optional[float] = Field(None, description="Average income over 5 years (CAD)")
    inc_growth: Optional[float] = Field(None, description="Income growth rate (decimal, e.g. 0.24 = 24%)")
    attractiveness_score: Optional[float] = Field(None, description="Composite attractiveness score (0-100)")
    attractiveness_category: Optional[str] = Field(None, description="Low / Moderate / High")

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────
# SCHEMAS DE RESPOSTA PAGINADA
# ─────────────────────────────────────────────────────────────

class PaginatedResponse(BaseModel):
    """
    Wrapper genérico para respostas paginadas.
    Toda listagem da API retorna neste formato para consistência.
    """
    total: int = Field(..., description="Total number of records available")
    page: int = Field(..., description="Current page number (1-indexed)")
    page_size: int = Field(..., description="Number of records per page")
    data: list = Field(..., description="List of records for this page")


# ─────────────────────────────────────────────────────────────
# SCHEMAS DE ERRO E SAÚDE
# ─────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    """
    Schema da resposta do endpoint de health check.
    Usado por sistemas de monitoramento para verificar se a API está viva.
    """
    status: str = Field(..., description="'ok' if API is healthy")
    version: str = Field(..., description="API version")
    datasets_loaded: dict = Field(..., description="Number of records per dataset")


class ErrorResponse(BaseModel):
    """
    Schema padrão de erro.
    Garante que todos os erros da API têm o mesmo formato.
    """
    error: str = Field(..., description="Error type")
    detail: str = Field(..., description="Human-readable error description")
