"""
Sprint 4 — API Layer
Camada: api_layer
Entry point da API FastAPI.

Segurança OWASP aplicada:
  - Rate limiting (slowapi): evita abuso e DDoS
  - CORS: controla quais origens podem consumir a API
  - Security headers: protege contra clickjacking, XSS, sniffing
  - Validação de input: feita automaticamente pelo Pydantic
  - Sem exposição de stack traces em produção
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from src.api.routers.occupations import router as occupations_router
from src.api.routers.occupations import gap_router
from src.api.routers.supply import router as supply_router
from src.api.routers.municipalities import router as municipalities_router
from src.api.dependencies import load_datasets

# ─────────────────────────────────────────────────────────────
# RATE LIMITER (OWASP: API Rate Limiting)
# ─────────────────────────────────────────────────────────────

# Identifica o cliente pelo IP para aplicar o limite
limiter = Limiter(key_func=get_remote_address)

# ─────────────────────────────────────────────────────────────
# APLICAÇÃO FASTAPI
# ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="AI Talent Gap in Alberta — API",
    description="""
## API de Análise do Talent Gap em IA — Alberta, Canadá

Fornece acesso aos dados analíticos do projeto AI Talent Gap in Alberta,
incluindo projeções ocupacionais (2023-2033), supply de graduados e
indicadores municipais.

### Datasets
- **513 ocupações** com projeções de demanda
- **5.643 registros** de talent gap (ocupação × ano)
- **184 programas** de graduação com métricas de renda
- **420 municípios** de Alberta

### Autenticação
Esta versão não requer autenticação (dados públicos).
Produção deve implementar OAuth2 ou API Keys.

### Rate Limiting
- **100 requests/minuto** por IP
- Retorna HTTP 429 quando excedido
    """,
    version="1.0.0",
    # Desabilita docs em produção (aqui mantemos para portfólio)
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─────────────────────────────────────────────────────────────
# MIDDLEWARES DE SEGURANÇA
# ─────────────────────────────────────────────────────────────

# Rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS (OWASP: Cross-Origin Resource Sharing)
# Em produção, substituir "*" pelo domínio real do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # dev origins
    allow_credentials=False,
    allow_methods=["GET"],       # API read-only: apenas GET
    allow_headers=["*"],
)


# Security headers middleware (OWASP: Security Headers)
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """
    Adiciona headers de segurança em todas as respostas.
    Protege contra clickjacking, XSS e content sniffing.
    """
    response = await call_next(request)

    # Impede que a página seja carregada em iframe (anti-clickjacking)
    response.headers["X-Frame-Options"] = "DENY"

    # Impede que o browser adivinhe o content-type (anti-sniffing)
    response.headers["X-Content-Type-Options"] = "nosniff"

    # Força HTTPS em produção
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    # Política de referrer: não vaza URL em requests externos
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    return response


# ─────────────────────────────────────────────────────────────
# ROUTERS
# ─────────────────────────────────────────────────────────────

# Prefixo /api/v1 é boa prática: permite versionar a API no futuro
app.include_router(occupations_router, prefix="/api/v1")
app.include_router(gap_router, prefix="/api/v1")
app.include_router(supply_router, prefix="/api/v1")
app.include_router(municipalities_router, prefix="/api/v1")


# ─────────────────────────────────────────────────────────────
# ENDPOINTS RAIZ
# ─────────────────────────────────────────────────────────────

@app.get("/", tags=["Root"])
@limiter.limit("100/minute")
async def root(request: Request):
    """Endpoint raiz com links de navegação."""
    return {
        "name": "AI Talent Gap in Alberta — API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "occupations": "/api/v1/occupations",
            "ai_adjacent": "/api/v1/occupations/ai-adjacent",
            "gaps": "/api/v1/gaps",
            "gap_summary": "/api/v1/gaps/summary",
            "gap_trend": "/api/v1/gaps/trend",
            "supply": "/api/v1/supply",
            "municipalities": "/api/v1/municipalities",
            "health": "/health",
        },
    }


@app.get("/health", tags=["Root"])
@limiter.limit("100/minute")
async def health_check(request: Request):
    """
    Health check endpoint.
    Verifica se a API está viva e os dados estão carregados.
    Usado por sistemas de monitoramento (ex: AWS ALB, Kubernetes).
    """
    try:
        datasets = load_datasets()
        return {
            "status": "ok",
            "version": "1.0.0",
            "datasets_loaded": {
                name: len(df) for name, df in datasets.items()
            },
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "detail": str(e)},
        )


# ─────────────────────────────────────────────────────────────
# HANDLER DE ERROS GLOBAL
# ─────────────────────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Captura qualquer erro não tratado e retorna resposta padronizada.
    OWASP: nunca expor stack traces ao cliente em produção.
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred. Please try again later.",
        },
    )
