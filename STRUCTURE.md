# 📁 Estrutura do Projeto

Guia visual da organização de arquivos e pastas.

---

## 🌳 Árvore de Diretórios

```
project/
│
├── 📄 README.md                    # Visão geral do projeto
├── 📄 STRUCTURE.md                 # Este arquivo
├── 📄 requirements.txt             # Dependências Python
├── 📄 .gitignore                   # Arquivos ignorados pelo Git
│
├── 🐍 run_full_pipeline.py         # Executa pipeline completo
├── 🐍 validate_pipeline.py         # Valida integridade do pipeline
│
├── 📂 data/                        # Dados do projeto
│   ├── 📂 raw/                     # Dados originais (5 arquivos)
│   ├── 📂 processed/               # Dados limpos (5 CSVs)
│   └── 📂 analytics/               # Star schema (5 tabelas)
│
├── 📂 src/                         # Código-fonte
│   ├── 📂 ingestion/               # Sprint 1: Carregamento
│   │   └── load_raw_data.py
│   │
│   ├── 📂 cleaning/                # Sprint 2: Limpeza
│   │   ├── clean_ai_profiles.py
│   │   ├── clean_graduate_outcomes.py
│   │   ├── clean_occupational_outlook.py
│   │   ├── clean_municipal_data.py
│   │   └── run_cleaning_pipeline.py
│   │
│   ├── 📂 modeling/                # Sprint 3: Modelagem
│   │   ├── build_dim_occupation.py
│   │   ├── build_dim_time.py
│   │   ├── build_dim_municipality.py
│   │   ├── build_fact_talent_gap.py
│   │   ├── build_supply_analysis.py
│   │   ├── run_modeling_pipeline.py
│   │   └── generate_insights_report.py
│   │
│   └── 📂 api/                     # Sprint 4: API REST (próximo)
│
├── 📂 docs/                        # Documentação
│   ├── 📄 INDEX.md                 # Índice da documentação
│   ├── 📄 context.md               # Estado atual do projeto
│   ├── 📄 dictionary.md            # Glossário técnico
│   ├── 📄 DATA_FLOW.md             # Fluxo de dados
│   ├── 📄 PROJECT_SUMMARY.md       # Resumo executivo
│   │
│   ├── 📂 guides/                  # Guias práticos
│   │   └── QUICKSTART.md
│   │
│   └── 📂 sprints/                 # Documentação por sprint
│       └── SPRINT3_CHECKLIST.md
│
├── 📂 outputs/                     # Resultados gerados
│   └── insights_report.txt
│
└── 📂 notebooks/                   # Jupyter notebooks (exploração)
```

---

## 📊 Camadas de Dados

### 1️⃣ Raw (data/raw/)
**Propósito:** Dados originais, nunca modificados

| Arquivo | Tamanho | Descrição |
|---------|---------|-----------|
| `ai_adjacent_profiles_final.csv` | 4 KB | 12 ocupações AI-adjacent |
| `jet-albertas-occupational-outlook-...xlsx` | 400 KB | Projeções 2023-2033 |
| `ae-labour-market-outcomes-...csv` | 22 KB | Resultados de graduados |
| `Businesses by municipality.csv` | 17 MB | Empresas por município |
| `Census employment by municipality.csv` | 1.6 MB | Emprego por município |

### 2️⃣ Processed (data/processed/)
**Propósito:** Dados limpos e padronizados

| Arquivo | Linhas | Descrição |
|---------|--------|-----------|
| `ai_profiles_clean.csv` | 12 | Salários separados, outlook_score |
| `occupational_outlook_clean.csv` | 5.643 | Excel reconstruído, métricas |
| `graduate_outcomes_clean.csv` | 184 | Percentuais convertidos, flags |
| `businesses_clean.csv` | 169.371 | Colunas nulas removidas |
| `census_employment_clean.csv` | 28.356 | Indicadores padronizados |

### 3️⃣ Analytics (data/analytics/)
**Propósito:** Star schema pronto para análise

| Arquivo | Linhas | Tipo | Descrição |
|---------|--------|------|-----------|
| `dim_occupation.csv` | 513 | Dimensão | Ocupações com atributos |
| `dim_time.csv` | 11 | Dimensão | Anos 2023-2033 |
| `dim_municipality.csv` | 420 | Dimensão | Municípios de Alberta |
| `fact_talent_gap.csv` | 5.643 | Fato | Métricas de gap |
| `supply_analysis.csv` | 184 | Análise | Supply de graduados |

---

## 🐍 Scripts Principais

### Raiz do Projeto

| Script | Propósito | Quando Usar |
|--------|-----------|-------------|
| `run_full_pipeline.py` | Executa tudo (raw → insights) | Primeira execução ou rebuild completo |
| `validate_pipeline.py` | Valida integridade | Após executar pipeline |

### Por Sprint

**Sprint 1 — Ingestion**
- `src/ingestion/load_raw_data.py` — Carrega e valida dados brutos

**Sprint 2 — Cleaning**
- `src/cleaning/run_cleaning_pipeline.py` — Orquestra limpeza de todos os datasets
- Scripts individuais para cada dataset

**Sprint 3 — Modeling**
- `src/modeling/run_modeling_pipeline.py` — Constrói star schema completo
- `src/modeling/generate_insights_report.py` — Gera relatório executivo
- Scripts individuais para cada tabela

---

## 📚 Documentação

### Arquivos Principais

| Arquivo | Propósito | Público |
|---------|-----------|---------|
| `README.md` | Visão geral | Todos |
| `docs/guides/QUICKSTART.md` | Início rápido | Novos usuários |
| `docs/context.md` | Estado atual | Desenvolvedores |
| `docs/dictionary.md` | Glossário | Aprendizado |
| `docs/DATA_FLOW.md` | Fluxo técnico | Engenheiros |
| `docs/PROJECT_SUMMARY.md` | Resumo executivo | Stakeholders |

### Navegação

**Começando:** `README.md` → `docs/guides/QUICKSTART.md`  
**Desenvolvendo:** `docs/context.md` → `docs/dictionary.md`  
**Entendendo:** `docs/DATA_FLOW.md` → `docs/PROJECT_SUMMARY.md`

---

## 🎯 Convenções de Nomenclatura

### Arquivos Python
- `load_*.py` — Carregamento de dados
- `clean_*.py` — Limpeza de datasets
- `build_*.py` — Construção de tabelas
- `run_*.py` — Orquestradores de pipeline
- `generate_*.py` — Geração de outputs

### Arquivos de Dados
- `*_clean.csv` — Dados processados
- `dim_*.csv` — Tabelas dimensão
- `fact_*.csv` — Tabelas fato
- `*_analysis.csv` — Tabelas analíticas

### Documentação
- `*.md` — Markdown
- `UPPERCASE.md` — Documentos principais (README, QUICKSTART)
- `lowercase.md` — Documentos técnicos (context, dictionary)

---

## 🔄 Fluxo de Trabalho

### Primeira Execução
```bash
1. pip install -r requirements.txt
2. py run_full_pipeline.py
3. py validate_pipeline.py
4. type outputs\insights_report.txt
```

### Desenvolvimento
```bash
# Modificar código em src/
# Testar módulo específico
py src/modeling/build_dim_occupation.py

# Validar
py validate_pipeline.py
```

### Exploração
```bash
# Abrir Jupyter
jupyter notebook

# Carregar dados
import pandas as pd
df = pd.read_csv("data/analytics/fact_talent_gap.csv")
```

---

## 📦 Tamanhos

| Camada | Arquivos | Tamanho Total |
|--------|----------|---------------|
| Raw | 5 | ~19 MB |
| Processed | 5 | ~19 MB |
| Analytics | 5 | ~770 KB |
| Código | 15 | ~50 KB |
| Docs | 10 | ~100 KB |

**Total do Projeto:** ~38 MB

---

## 🚀 Próximas Adições

**Sprint 4:**
- `src/api/main.py` — FastAPI entry point com segurança OWASP
- `src/api/dependencies.py` — Injeção de dependências e paginação
- `src/api/models/schemas.py` — Schemas Pydantic
- `src/api/routers/` — Routers: occupations, supply, municipalities
- `test_api.py` — Testes funcionais

**Sprint 5:**
- `frontend/` — React/Nuxt app
- `frontend/components/` — UI components
- `frontend/pages/` — Dashboard pages

---

**Última atualização:** Sprint 4  
**Próxima atualização:** Sprint 5 (Frontend Dashboard)
