# Customer Intelligence & Campaign Orchestration Platform (CICOP)

A full-stack customer intelligence system combining a **FastAPI backend**, **Streamlit dashboard**, **ML-powered segmentation & recommendations**, and a **business rules campaign engine**.

---

## Quick Start

```powershell
# 1. Create virtual environment and install dependencies
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Copy environment file
copy .env.example .env

# 3. Initialise database and generate sample data
python backend\scripts\setup_database.py
python backend\scripts\generate_standalone_data.py

# 4. Start all services (Windows)
backend\scripts\start_all_services.cmd
```

> **Linux/Mac:** use `bash backend/scripts/start_dev.sh`

---

## Service URLs

| Service | URL |
|---|---|
| Streamlit Dashboard | http://localhost:8501 |
| FastAPI Main | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| ML Model Server | http://localhost:8001 |
| API Gateway | http://localhost:8002 |

---

## Start Individual Services

```powershell
# FastAPI main API
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload

# ML Model Server
uvicorn backend.ml.model_server:app --host 0.0.0.0 --port 8001 --reload

# API Gateway
uvicorn backend.api.gateway:app --host 0.0.0.0 --port 8002 --reload

# Streamlit Dashboard
streamlit run frontend\app.py --server.port=8501
```

---

## Repository Structure

```
Customer-Intelligence-Platform/
├── backend/                    # All server-side Python code
│   ├── api/                    # FastAPI application + gateway
│   ├── auth/                   # JWT authentication
│   ├── config/                 # YAML configs + CI/CD workflow
│   ├── data/                   # Database manager, loader, preprocessor
│   ├── ml/                     # Segmentation, recommendations, model server
│   ├── models/                 # Serialised model artefacts
│   ├── rules/                  # Campaign rules engine & orchestrator
│   ├── scripts/                # Setup, ETL, training, migration scripts
│   ├── tests/                  # pytest unit tests
│   ├── utils/                  # Logger, config loader, helpers, validation
│   └── workers/                # Celery async task workers
│
├── frontend/                   # Streamlit dashboard
│   ├── app.py                  # Main multi-page application
│   ├── components/             # KPI cards, charts, filters, sidebar
│   └── utils/                  # Dashboard data aggregation
│
├── Dockerfile                  # Multi-stage Docker build
├── requirements.txt            # Python dependencies
├── .env                        # Local environment variables
├── .env.example                # Environment template
├── .gitignore
├── TECHNICAL.md                # Full technical reference (17 sections)
└── README.md                   # This file
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI + Uvicorn |
| Frontend | Streamlit + Plotly |
| ML | scikit-learn (K-Means, DBSCAN, GBM) |
| Database | SQLite (default) / PostgreSQL |
| Async Workers | Celery + Redis |
| Authentication | JWT (python-jose) |
| Containerisation | Docker |
| CI/CD | GitHub Actions |

---

## Features

- **Customer 360 Data Foundation** — Comprehensive temporal feature engineering (recency, frequency, spend, returns).
- **V1 Next-Purchase Propensity (Frozen)** — GradientBoosting model identifying customer purchase probability over the next 30 days.
- **Behavioral Segmentation (Frozen)** — K-Means clustering isolating Dormant Multi-Buyers, Active High-Value, Recent Repeat Buyers, and One-Time Dormant cohorts.
- **Segment × Propensity Intelligence (Phase 3)** — Combination matrix marrying short-term propensity with long-term behavioral segments.
- **Deterministic Action Policy (Phase 4)** — Rules-based engine (no LLM) evaluating Segment, Propensity, and Behavioral Signals to generate deterministic recommendations and confidence scores.
- *Note: Phase 4 is implemented as an independent experimental intelligence layer. Production API/Dashboard integration (Phase 5) is NOT yet implemented.*

### Legacy Application Features (Pre-Phase 1)
- **Interactive Dashboard** — KPI cards, trend charts, category/segment breakdown.
- **Business Rules Engine** — Legacy campaign eligibility rules (untouched by Phase 4).
- **REST API** — Full CRUD for customers, transactions, campaigns.

---

## Environment Variables

Copy `.env.example` to `.env` and configure:

```env
DATABASE_URL=sqlite:///backend/data/customer_insights.db
JWT_SECRET_KEY=your-secret-key-here
ML_SERVING_URL=http://localhost:8001
GATEWAY_URL=http://localhost:8002
MODEL_DIR=backend/models
REDIS_URL=redis://localhost:6379/0
```

See `TECHNICAL.md` §4 for the full environment variable reference.

---

## Running Tests

```powershell
# From workspace root
pytest backend/tests/ -v

# With coverage
pytest backend/tests/ -v --cov=backend --cov=frontend --cov-report=html
```

---

## Docker

```bash
# Build and run
docker build --target base -t cicop:latest .
docker run -p 8000:8000 -p 8501:8501 --env-file .env cicop:latest
```

---

## Full Technical Documentation

See **[TECHNICAL.md](./TECHNICAL.md)** for detailed coverage of:
1. Project overview
2. Repository structure
3. Technology stack
4. Environment variables
5. Service architecture
6. Database schema
7. API endpoints
8. ML pipeline
9. Business rules engine
10. Authentication
11. Configuration system
12. Logging
13. Development setup
14. Testing
15. Deployment
16. Data pipeline
17. Known issues & limitations