# AI Talent Gap in Alberta

End-to-end data engineering project analyzing the gap between AI talent demand and supply in Alberta, Canada (2023–2033).

Built by [Flávio Tavares](https://www.linkedin.com/in/fl%C3%A1vio-tavares-31080518b/)

## Overview

This project investigates the mismatch between occupational demand and graduate supply in AI-adjacent roles across Alberta, using real public datasets from the Government of Alberta and Statistics Canada.

**Key findings:**
- Database Analysts have the highest gap (Index: 69.2, 4.5x more openings than candidates)
- 896 AI-related graduates/year vs ~230 AI-adjacent job openings/year — a skills mismatch, not a volume problem
- The gap grew 3% from 2023 to 2033, indicating a structural issue

## Architecture

```
data/raw/          →   data/processed/   →   data/analytics/   →   API + Dashboard
  5 source files        5 cleaned CSVs        Star schema            FastAPI + Next.js
```

### Star Schema
- `dim_occupation` — 513 occupations
- `dim_time` — 11 years (2023–2033)
- `dim_municipality` — 420 municipalities
- `fact_talent_gap` — 5,643 records with AI Talent Gap Index
- `supply_analysis` — 184 graduate programs

## Stack

| Layer | Technology |
|-------|-----------|
| Data processing | Python 3.14, pandas, openpyxl |
| API | FastAPI, Pydantic, slowapi |
| Frontend | Next.js 15, TypeScript, Tailwind CSS, Recharts |
| Deploy | Railway |

## Running Locally

**1. Install dependencies**
```bash
pip install -r requirements.txt
cd frontend && npm install
```

**2. Run the full ETL pipeline**
```bash
py run_full_pipeline.py
```

**3. Start the API**
```bash
uvicorn src.api.main:app --reload
# http://localhost:8000/docs
```

**4. Start the frontend**
```bash
cd frontend
npm run dev
# http://localhost:3000
```

## Project Structure

```
├── src/
│   ├── ingestion/       # Sprint 1: Load raw data
│   ├── cleaning/        # Sprint 2: Clean & transform
│   ├── modeling/        # Sprint 3: Star schema + metrics
│   └── api/             # Sprint 4: REST API (FastAPI)
├── frontend/            # Sprint 5: Next.js dashboard
├── data/
│   ├── raw/             # Original source files (not tracked)
│   ├── processed/       # Cleaned CSVs (not tracked)
│   └── analytics/       # Star schema tables (not tracked)
├── docs/
│   └── dictionary.md    # Glossary of 50+ technical terms
├── run_full_pipeline.py
├── validate_pipeline.py
└── requirements.txt
```

## Datasets

All data is real and publicly available:
- [Alberta Occupational Outlook 2023–2033](https://open.alberta.ca)
- [Graduate Outcomes — Post-Secondary Institutions 2024](https://open.alberta.ca)
- Census Employment by Municipality (Statistics Canada)
- Businesses by Municipality (Statistics Canada)
- AI-Adjacent Profiles (ALIS OCCinfo)

## Sprints

| Sprint | Description | Status |
|--------|-------------|--------|
| 1 | Data Ingestion | ✅ Done |
| 2 | Data Cleaning | ✅ Done |
| 3 | Dimensional Modeling | ✅ Done |
| 4 | REST API (FastAPI + OWASP security) | ✅ Done |
| 5 | Interactive Dashboard (Next.js) | ✅ Done |

## License

Educational project — public data from the Government of Alberta.
