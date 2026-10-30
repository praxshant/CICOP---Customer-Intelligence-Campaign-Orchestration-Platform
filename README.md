# Customer Intelligence & Campaign Orchestration Platform (CICOP)

CICOP is a Python customer-intelligence prototype with a Streamlit dashboard, a FastAPI service, a separate ML scoring service, deterministic campaign rules, and reproducible training artefacts.

## What is currently wired

```text
Streamlit dashboard (:8501) ──reads/writes──> SQLite or PostgreSQL
        │
        └── POST /predict ──> API gateway (:8002) ──> ML server (:8001)

FastAPI main service (:8000) ──> SQLite or PostgreSQL
```

The dashboard currently uses the shared data layer directly for dashboard, segmentation, and campaign screens. Its prediction demo is the only browser-to-service path: it calls the gateway, which proxies to the ML server. The authenticated FastAPI endpoints are available for API consumers, but are not the dashboard’s data source. This is intentional in the present prototype and should be changed to REST-only access before a multi-user deployment.

## Quick start (Windows)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env

python backend\scripts\setup_database.py
python backend\scripts\generate_standalone_data.py
backend\scripts\start_all_services.cmd
```

For Linux/macOS, use `bash backend/scripts/start_dev.sh` after installing the dependencies.

| Service | URL |
|---|---|
| Dashboard | http://localhost:8501 |
| Main API / OpenAPI docs | http://localhost:8000 / http://localhost:8000/docs |
| ML server | http://localhost:8001 |
| Gateway | http://localhost:8002 |

The ML server returns a clearly marked placeholder score when no model artefact has been deployed. Do not treat that fallback as a trained prediction.

## Configuration

Copy `.env.example` and set at least the following values for your environment:

```env
DATABASE_URL=sqlite:///backend/data/customer_insights.db
ML_SERVING_URL=http://localhost:8001
GATEWAY_URL=http://localhost:8002
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=replace-this-before-deployment
```

Redis enables API rate limiting. When it is unavailable, the API starts and logs in safely without rate limiting; production deployments should run Redis. The main API also creates its `users` table at startup. Provision users through the authentication schema before using protected endpoints; no registration UI is included.

## Tests

```powershell
pytest backend/tests -q
python -m compileall -q backend frontend
```

## Training and validation evidence

The tracked notebooks, plots, and JSON reports in `backend/training/` are the source of truth for the following results:

- Data preparation processed 1,067,371 raw Online Retail II rows into 1,033,031 prepared transactions; all preparation checks passed.
- The temporal dataset contains 71,647 observations across 5,247 customers (41,749 train / 14,468 validation / 15,430 test). Data foundation, leakage, target-window, split, and reproducibility gates all passed.
- The selected 30-day next-purchase experiment is `HistGradientBoosting_Tuned`: test ROC-AUC **0.8191**, PR-AUC **0.5627**, Brier score **0.1098**, and Lift@10% **3.648**. Its operating threshold is 0.30; it is a frozen experimental result, not deployed by `backend/ml/model_server.py`.
- Segmentation selected four operationally interpretable K-Means cohorts: Dormant Multi-Buyers (32.91%), Active High-Value (10.90%), Recent Repeat Buyers (24.07%), and One-Time Dormant (32.11%). The phase-2 report remains marked as awaiting human review.
- Phase 3’s segment × propensity matrix and Phase 4’s deterministic action-policy validation are complete. Phase 4 produced valid recommendations for all 5,247 scored customers, with no duplicate customer rows, fallback recommendations, or serialization failures.

These reports use historical retail data and are not equivalent to an online production evaluation. The training intelligence layers are not yet integrated into the deployed dashboard/API workflow.

## Repository hygiene

Source code, configurations, tests, notebooks, validation reports, and visual training artefacts are tracked. Local databases, raw datasets, model binaries, logs, exports, caches, and secrets are intentionally ignored by Git. Do not commit `.env`, generated databases, raw source data, model artefacts, logs, or `__pycache__` directories.

## Further detail

See [TECHNICAL.md](TECHNICAL.md) for architecture, endpoint, audit, and training-report details.
