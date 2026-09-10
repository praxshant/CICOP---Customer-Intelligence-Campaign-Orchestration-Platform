# TECHNICAL REFERENCE — Customer Intelligence & Campaign Orchestration Platform (CICOP)

> **Status:** Active Development · **Version:** 1.1.0 · **Updated:** 2026-08-23

---

## 1. Project Overview

CICOP is a full-stack customer intelligence platform combining:

- **FastAPI backend** exposing REST APIs for customers, transactions, ML predictions, and campaigns.
- **Streamlit frontend** dashboard providing interactive KPI cards, charts, segmentation views, and campaign management.
- **ML pipeline** for customer segmentation (K-Means, DBSCAN, Gaussian Mixture), collaborative-filtering recommendations, and a trained GradientBoosting model artifact.
- **Business rules engine** that applies loyalty, win-back, cross-sell, and seasonal campaign logic.
- **Celery workers** for async model retraining and ML-server reload scheduling (requires Redis).
- **SQLite** as the default database (PostgreSQL supported via `DATABASE_URL`).

---

## 2. Repository Structure

```
Customer-Intelligence-Platform/
├── backend/                    # All server-side Python code
│   ├── api/                    # FastAPI app + API gateway
│   │   ├── main.py             # Primary FastAPI application (port 8000)
│   │   └── gateway.py          # API gateway / reverse proxy (port 8002)
│   ├── auth/
│   │   └── auth_manager.py     # JWT authentication manager
│   ├── config/                 # YAML configs + CI/CD + Action Policy
│   │   ├── config.yaml         # Main app config
│   │   ├── database_config.yaml
│   │   ├── ml_config.yaml
│   │   ├── intelligence_action_policy.json  # Phase 4 action policy configuration
│   │   └── ci-cd.yml           # GitHub Actions workflow
│   ├── data/                   # Data layer
│   │   ├── database_manager.py # SQLite/PostgreSQL connection & ORM
│   │   ├── data_loader.py      # CSV/JSON/Excel data ingestion
│   │   └── data_preprocessor.py# Cleaning, feature engineering
│   ├── ml/                     # Machine learning layer
│   │   ├── customer_segmentation.py  # K-Means / DBSCAN / GMM segmentation
│   │   ├── intelligence_engine.py    # Phase 4 Why+What Next+Confidence+Evidence
│   │   ├── recommendation_engine.py  # Collaborative filtering recommendations
│   │   ├── model_server.py           # ML serving FastAPI app (port 8001)
│   │   ├── training.py               # GradientBoosting training pipeline
│   │   ├── advanced_models.py        # Advanced clustering models
│   │   └── model_utils.py            # Model persistence utilities
│   ├── models/                 # Serialised model artefacts (.pkl)
│   ├── monitoring/             # Health & metrics (Prometheus)
│   ├── nginx/                  # Nginx configs
│   ├── rules/                  # Business rules & campaign engine
│   │   ├── rules_engine.py     # Core eligibility & rule evaluation (legacy)
│   │   ├── action_policy.py    # Phase 4 deterministic action policy
│   │   ├── campaign_generator.py     # Personalised campaign generation
│   │   └── campaign_orchestrator.py  # Multi-channel orchestration + A/B tests
│   ├── scripts/                # Operational scripts
│   │   ├── setup_database.py   # DB initialisation script
│   │   ├── generate_standalone_data.py  # Sample data generator
│   │   ├── run_etl.py          # Full ETL pipeline
│   │   ├── train_model.py      # ML model training CLI
│   │   ├── migrate_to_postgres.py    # SQLite → PostgreSQL migration
│   │   ├── start_dev.sh        # Linux/Mac dev startup
│   │   ├── run_etl.cmd         # Windows ETL runner
│   │   └── start_all_services.cmd   # Windows all-services launcher
│   ├── tests/                  # Unit tests (pytest)
│   │   ├── test_data_processing.py
│   │   ├── test_rules_engine.py
│   │   ├── test_segmentation.py
│   │   └── test_intelligence_engine.py  # Phase 4 tests
│   ├── utils/                  # Shared utilities
│   │   ├── logger.py           # Structured logging setup
│   │   ├── config_loader.py    # YAML config loader with defaults
│   │   ├── helpers.py          # Date helpers, formatters, colour palettes
│   │   ├── validation.py       # Input validation decorators
│   │   ├── json_encoder.py     # NumPy/Pandas → JSON serialisation
│   │   ├── circuit_breaker.py  # Circuit breaker pattern
│   │   └── recovery.py         # Alert & recovery utilities
│   └── workers/
│       └── celery_app.py       # Celery tasks: retrain + reload ML server
│
├── frontend/                   # Streamlit dashboard
│   ├── app.py                  # Main Streamlit application (port 8501)
│   ├── components/             # Reusable UI components
│   │   ├── kpi_cards.py        # Revenue / transaction KPI cards
│   │   ├── charts.py           # Plotly chart components
│   │   ├── filters.py          # Date / category / segment filters
│   │   └── sidebar.py          # Navigation sidebar
│   ├── utils/
│   │   └── data_utils.py       # Dashboard data aggregation helpers
│   └── assets/                 # Static assets (logos, CSS)
│
├── Dockerfile                  # Multi-stage Docker build
├── requirements.txt            # Python dependencies
├── .env                        # Local environment variables (not committed)
├── .env.example                # Environment template
├── .gitignore
├── README.md                   # Quick-start guide
└── TECHNICAL.md                # This document
```

---

## 3. Technology Stack

| Layer | Technology | Version |
|---|---|---|
| Language | Python | 3.11 |
| Backend API | FastAPI | ≥0.104 |
| ASGI server | Uvicorn | ≥0.24 |
| Frontend | Streamlit | ≥1.28 |
| Charting | Plotly | ≥5.18 |
| ML / Data | scikit-learn, pandas, numpy | Latest stable |
| Model persistence | joblib, pickle | stdlib / joblib |
| Database (default) | SQLite | stdlib |
| Database (optional) | PostgreSQL | ≥13 |
| ORM / driver | SQLAlchemy, psycopg2 | ≥2.0 |
| Async tasks | Celery | ≥5.3 |
| Message broker | Redis | ≥7 |
| Authentication | JWT (python-jose) | ≥3.3 |
| HTTP client | httpx, requests | ≥0.25 |
| Containerisation | Docker | ≥24 |
| CI/CD | GitHub Actions | — |

---

## 4. Environment Variables

All environment variables are loaded from `.env` at workspace root.

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///backend/data/customer_insights.db` | Database connection string |
| `SECRET_KEY` | (set in .env) | App secret for session signing |
| `JWT_SECRET_KEY` | (set in .env) | JWT signing key |
| `ML_SERVING_URL` | `http://localhost:8001` | URL of ML model server |
| `GATEWAY_URL` | `http://localhost:8002` | URL of API gateway |
| `MODEL_DIR` | `backend/models` | Directory for model artefacts |
| `MODEL_PATH` | `backend/models/model.pkl` | Path to primary model |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis for Celery broker |
| `CELERY_BROKER_URL` | same as `REDIS_URL` | Celery broker URL |
| `CELERY_RESULT_BACKEND` | same as `REDIS_URL` | Celery result backend |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `ENVIRONMENT` | `development` | `development` / `production` |
| `DEBUG` | `True` | Enable debug mode |

---

## 5. Service Architecture

```
                      ┌─────────────────────────────────┐
                      │    Streamlit Dashboard :8501     │
                      │    frontend/app.py               │
                      └───────────────┬─────────────────┘
                                      │ HTTP requests
              ┌───────────────────────▼──────────────────┐
              │         API Gateway :8002                 │
              │         backend/api/gateway.py            │
              └──────────┬────────────────┬──────────────┘
                         │                │
         ┌───────────────▼──┐    ┌────────▼──────────────┐
         │  FastAPI API :8000│    │  ML Model Server :8001 │
         │  backend/api/     │    │  backend/ml/           │
         │  main.py          │    │  model_server.py       │
         └───────┬───────────┘    └────────────────────────┘
                 │
         ┌───────▼───────────┐         ┌──────────────────┐
         │  Database Layer   │         │  Celery Worker   │
         │  SQLite / Postgres│         │  + Redis Broker  │
         └───────────────────┘         └──────────────────┘
```

---

## 6. Database Schema

**Default:** SQLite at `backend/data/customer_insights.db`  
**PostgreSQL:** Set `DATABASE_URL=postgresql://user:pass@host/db`

### Tables

#### `customers`
| Column | Type | Description |
|---|---|---|
| `customer_id` | TEXT (PK) | Unique identifier, e.g. `CUST_000001` |
| `first_name` | TEXT | |
| `last_name` | TEXT | |
| `email` | TEXT | |
| `registration_date` | DATE | |
| `age` | INTEGER | |
| `gender` | TEXT | |
| `location` | TEXT | City, State |
| `segment_name` | TEXT | Populated after segmentation run |

#### `transactions`
| Column | Type | Description |
|---|---|---|
| `transaction_id` | TEXT (PK) | e.g. `TXN_00000001` |
| `customer_id` | TEXT (FK) | References `customers` |
| `transaction_date` | DATE | |
| `amount` | REAL | Transaction amount in USD |
| `category` | TEXT | e.g. Food & Dining, Shopping |
| `subcategory` | TEXT | |
| `merchant` | TEXT | |
| `payment_method` | TEXT | Credit Card, PayPal, etc. |

#### `customer_segments`
| Column | Type | Description |
|---|---|---|
| `customer_id` | TEXT (PK/FK) | |
| `segment_id` | INTEGER | Cluster label |
| `segment_name` | TEXT | Human-readable e.g. High-Value-Frequent-Active |
| `last_updated` | DATE | |

#### `campaigns`
| Column | Type | Description |
|---|---|---|
| `campaign_id` | TEXT (PK) | e.g. `CAMP_000001` |
| `customer_id` | TEXT (FK) | |
| `campaign_type` | TEXT | loyalty_reward / win_back / cross_sell / seasonal_promotion |
| `offer_description` | TEXT | |
| `discount_amount` | REAL | |
| `created_date` | DATE | |
| `status` | TEXT | active / sent / expired |

### Indexes
- `idx_transactions_customer_id`
- `idx_transactions_date`
- `idx_transactions_category`
- `idx_customers_email`
- `idx_customers_location`

---

## 7. API Endpoints

### FastAPI Main (`backend/api/main.py` — port 8000)

| Method | Path | Description |
|---|---|---|
| GET | `/` | Health / version info |
| GET | `/health` | Health check |
| POST | `/auth/login` | Get JWT token |
| POST | `/auth/refresh` | Refresh JWT token |
| GET | `/customers` | List customers (paginated) |
| GET | `/customers/{id}` | Get single customer |
| GET | `/customers/{id}/transactions` | Customer transaction history |
| GET | `/customers/{id}/segments` | Customer segment info |
| GET | `/transactions` | List transactions (paginated, filterable) |
| POST | `/transactions` | Create transaction |
| GET | `/analytics/overview` | Dashboard KPIs |
| GET | `/analytics/segments` | Segment analytics |
| GET | `/analytics/categories` | Category breakdown |
| POST | `/ml/segment` | Run segmentation on POSTed features |
| POST | `/ml/recommend` | Get recommendations for customer |
| POST | `/ml/predict` | ML model prediction |
| GET | `/campaigns` | List campaigns |
| POST | `/campaigns/generate` | Generate campaigns for segment |
| GET | `/campaigns/{id}` | Get campaign details |

### ML Model Server (`backend/ml/model_server.py` — port 8001)

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/predict` | Feature vector → prediction |
| POST | `/reload_model` | Hot-reload model from disk |

### API Gateway (`backend/api/gateway.py` — port 8002)

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Gateway health |
| POST | `/predict` | Proxy to ML server `/predict` |

---

## 8. ML Pipeline

### Customer Segmentation (`backend/ml/customer_segmentation.py`)

**Input features** (created by `DataPreprocessor.create_customer_features()`):

| Feature | Description |
|---|---|
| `total_spent` | Lifetime transaction total |
| `avg_transaction_amount` | Mean transaction value |
| `transaction_count` | Number of transactions |
| `avg_monthly_spend` | Normalised monthly spend |
| `transaction_frequency` | Transactions per day |
| `recency_days` | Days since last transaction |
| `unique_merchants` | Distinct merchants visited |

**Algorithms available:**
- `kmeans` (default) — `sklearn.cluster.KMeans`
- `dbscan` — `sklearn.cluster.DBSCAN`
- `gmm` — `sklearn.mixture.GaussianMixture`

**Optimal cluster selection:** Elbow method + Silhouette scoring combined.

**Segment naming:** Rule-based on cluster centroid values (high spend + low recency → "High-Value-Frequent-Active" etc.)

### Recommendation Engine (`backend/ml/recommendation_engine.py`)

- Builds a customer × category matrix from transaction history.
- Computes cosine similarity between customers.
- Returns top-N category recommendations for a given customer ID.

### GradientBoosting Model (`backend/ml/training.py`)

- **Target:** Binary classifier — whether transaction amount > customer median.
- **Features:** `amount`, `cat_count`, `recency_days`
- **Model:** `sklearn.ensemble.GradientBoostingClassifier`
- **Artefact:** Saved to `MODEL_DIR/model.pkl` via `joblib`
- **Metrics reported:** Accuracy, AUC-ROC

---

## 9. Business Rules Engine

### Campaign Types (`backend/rules/rules_engine.py`)

| Campaign Type | Eligibility Conditions | Offer |
|---|---|---|
| `loyalty_reward` | total_spent ≥ $1000, transactions ≥ 10, recency ≤ 30d | 15% off, min $100 |
| `win_back` | recency ≥ 90d, total_spent ≥ $500 | 25% off, min $50 |
| `cross_sell` | unique_merchants ≥ 2, avg_amount ≥ $50 | 20% off, min $75 |
| `seasonal_promotion` | seasonal_multiplier ≥ 1.2 | 10% off, min $60 |

### Campaign Priority Scoring
- Base scores: loyalty_reward=0.9, win_back=0.7, cross_sell=0.6, seasonal=0.5
- Multiplied by: spend tier (1.1–1.2x for high-value) and recency (1.1x if < 30 days)
- Capped at 1.0

### Multi-Channel Orchestration (`backend/rules/campaign_orchestrator.py`)
- Channels: email, SMS, push, social
- A/B testing: 3-variant split (control + 2 variants)
- Scheduling: channel-optimal timing (email 09:00, SMS 12:00, push 18:00)

---

## 10. Authentication

- **Provider:** JWT via `python-jose`
- **Token types:** Access token (short-lived) + refresh token
- **Secret:** `JWT_SECRET_KEY` env var
- **Auth manager:** `backend/auth/auth_manager.py`
- **Protected endpoints:** All `/customers`, `/transactions`, `/analytics`, `/campaigns`, `/ml` routes require `Authorization: Bearer <token>`

---

## 11. Configuration System

Config is loaded via `backend/utils/config_loader.py`:

1. **Priority:** environment variable `DATABASE_URL` etc. → YAML file → hardcoded defaults.
2. **Main config:** `backend/config/config.yaml`
3. **DB config:** `backend/config/database_config.yaml`
4. **ML config:** `backend/config/ml_config.yaml`

If config files are missing, the loader returns safe defaults (SQLite, 5 segments, INFO logging).

---

## 12. Logging

- **Module:** `backend/utils/logger.py` via `setup_logger(name)`
- **Format:** JSON-structured with timestamp, level, module, message
- **Output:** stdout + rotating file handler
- **File location:** `backend/logs/<name>.log`
- **Level:** Controlled by `LOG_LEVEL` env var (default: `INFO`)

---

## 13. Development Setup

### Prerequisites
- Python 3.11+
- pip or conda
- (Optional) Redis for Celery workers
- (Optional) PostgreSQL for production DB

### Quick Start

```powershell
# 1. Clone and enter repository
cd Customer-Intelligence-Platform

# 2. Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment file
copy .env.example .env

# 5. Initialise database and generate sample data
python backend\scripts\setup_database.py
python backend\scripts\generate_standalone_data.py

# 6. Start all services (Windows)
backend\scripts\start_all_services.cmd
```

### Start individual services

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

### Service URLs

| Service | URL |
|---|---|
| Streamlit Dashboard | http://localhost:8501 |
| FastAPI Main | http://localhost:8000 |
| FastAPI Docs (Swagger) | http://localhost:8000/docs |
| ML Model Server | http://localhost:8001 |
| API Gateway | http://localhost:8002 |

---

## 14. Testing

### Run all tests

```powershell
# From workspace root
pytest backend/tests/ -v
```

### Run with coverage

```powershell
pytest backend/tests/ -v --cov=backend --cov=frontend --cov-report=html
```

### Test modules

| File | Coverage |
|---|---|
| `backend/tests/test_data_processing.py` | DataLoader, DataPreprocessor, DatabaseManager |
| `backend/tests/test_rules_engine.py` | RulesEngine, CampaignGenerator |
| `backend/tests/test_segmentation.py` | CustomerSegmentation |

---

## 15. Deployment

### Docker

```bash
# Build base image
docker build --target base -t cicop:latest .

# Run API + dashboard together
docker run -p 8000:8000 -p 8501:8501 \
  --env-file .env \
  cicop:latest

# Run individual stages
docker build --target ml-serving -t cicop-ml:latest .
docker run -p 8001:8001 cicop-ml:latest

docker build --target api-gateway -t cicop-gateway:latest .
docker run -p 8002:8002 cicop-gateway:latest

docker build --target worker -t cicop-worker:latest .
docker run cicop-worker:latest
```

### PostgreSQL Production Setup

```bash
# 1. Set DATABASE_URL in .env
DATABASE_URL=postgresql://cicop_user:cicop_pass@localhost:5432/cicop_db

# 2. Run database setup
python backend/scripts/setup_database.py

# 3. (Optional) Migrate from SQLite
python backend/scripts/migrate_to_postgres.py
```

### Celery Workers (requires Redis)

```bash
# Start Redis
docker run -d -p 6379:6379 redis:7

# Start Celery worker
celery -A backend.workers.celery_app worker --loglevel=info

# Start Celery beat scheduler
celery -A backend.workers.celery_app beat --loglevel=info
```

### CI/CD

GitHub Actions workflow at `backend/config/ci-cd.yml`:
- Triggers on push to `main` / `develop`, and PRs to `main`
- Steps: install deps → setup DB → pytest → flake8 lint → bandit security scan → build

---

## 16. Data Pipeline

### ETL Flow

```
Raw Data Sources (CSV/JSON/Excel)
        ↓
DataLoader.load_sample_data()
        ↓
DataPreprocessor.clean_transaction_data()
  → remove duplicates, negative amounts, future dates
  → normalise category case
  → fill missing subcategory / payment_method
        ↓
DataPreprocessor.create_customer_features()
  → total_spent, avg_transaction_amount, transaction_count
  → avg_monthly_spend, transaction_frequency, recency_days
  → unique_merchants, primary_category, spending_std
        ↓
CustomerSegmentation.perform_segmentation()
  → StandardScaler → KMeans(n_clusters=optimal)
  → segment naming by centroid analysis
        ↓
DatabaseManager (SQLite / PostgreSQL)
  → insert customers, transactions, segments, campaigns
```

### Sample Data Generator

`backend/scripts/generate_standalone_data.py` creates:
- **1,000 customers** with realistic demographics (name, email, age, location)
- **~15,000 transactions** across 8 spending categories with seasonal multipliers
- **Segment assignments** based on spending thresholds
- **Campaigns** per segment type

---

## 17. Known Issues & Limitations

### Current Limitations

1. **Authentication not enforced on all routes** — JWT middleware is scaffolded but not globally applied. Individual routes do protect with `Depends(get_current_user)`.

2. **Celery tasks require Redis** — Running `celery_app.py` without Redis will fail at import-time broker connection. Workers are optional for local dev.

3. **ML model cold start** — The model server returns an error until a model artefact exists at `MODEL_PATH`. Run `python backend/scripts/train_model.py` first.

4. **PostgreSQL migration** — `migrate_to_postgres.py` requires `psycopg2` and a running Postgres instance. Not needed for SQLite-based development.

5. **Streamlit session state** — Dashboard data is cached in `st.session_state`. A page refresh reloads from DB; no real-time streaming.

6. **Multi-stage Docker build** — Stages `ml-serving`, `api-gateway`, `worker`, `frontend` reference `FROM base` which is defined in stage 1 (`FROM python:3.11-slim as base`). Ensure you build with `--target <stage>` or build the full image.

### Import Resolution

All modules use absolute `backend.*` / `frontend.*` imports. The workspace root must be in `PYTHONPATH` (or `sys.path`). When running via `uvicorn backend.api.main:app` from the workspace root, Python resolves correctly.

```powershell
# Set PYTHONPATH explicitly if needed
$env:PYTHONPATH = "C:\path\to\Customer-Intelligence-Platform"
```

---

## 18. ML Intelligence Audit

> **Audit date:** 2026-08-17  
> All metrics in this section were measured against the live `backend/data/customer_insights.db` database (1,000 customers, 14,881 transactions) using the current training code. No metrics were estimated or inferred.

---

### 18.1 ML Model Inventory

| Model | File | Algorithm | Artifact | Runtime | API | Dashboard | Campaign | Status |
|---|---|---|---|---|---|---|---|---|
| GradientBoosting Classifier | `backend/ml/training.py` | `sklearn.GradientBoostingClassifier` | `backend/models/model.pkl` (134 KB) | Loaded by `model_server.py` on startup | `POST /predict` (model server) | No | No | **ACTIVE — trained, served** |
| K-Means Customer Segmentation | `backend/ml/customer_segmentation.py` | `sklearn.cluster.KMeans` | None (trained in-memory on demand) | Called from `POST /segmentation` in `main.py` | `POST /segmentation` | Yes (segment view) | Yes (segment → campaign type) | **ACTIVE — no persisted artifact** |
| Collaborative Filtering Recommendations | `backend/ml/recommendation_engine.py` | Cosine similarity on customer×category matrix | None (computed in-memory) | Not wired to any API endpoint | No | No | No | **IMPLEMENTED but NOT WIRED to API or dashboard** |
| DBSCAN Clustering | `backend/ml/customer_segmentation.py` | `sklearn.cluster.DBSCAN` | None | Not called from any API or script | No | No | No | **DEAD CODE — available but never invoked** |
| Gaussian Mixture Model (GMM) | referenced in doc only | `sklearn.mixture.GaussianMixture` | None | Not present in any file | No | No | No | **NOT IMPLEMENTED** |
| AdvancedClusteringModel (ensemble) | `backend/ml/advanced_models.py` | KMeans + DBSCAN + Agglomerative + Spectral | None | Not called from anywhere | No | No | No | **DEAD CODE** |
| DeepLearningModel (TF/MLP) | `backend/ml/advanced_models.py` | TensorFlow/Keras or sklearn MLP | None | Not called from anywhere; TF not installed | No | No | No | **DEAD CODE — TF not available** |
| EnsembleModel | `backend/ml/advanced_models.py` | VotingClassifier (RF + GBM + NN) | None | Not called from anywhere | No | No | No | **DEAD CODE** |
| AutoMLModel | `backend/ml/advanced_models.py` | GridSearchCV over RF/GBM | None | Not called from anywhere | No | No | No | **DEAD CODE** |
| Business Rules Engine | `backend/rules/rules_engine.py` | Deterministic rule evaluation | None | Called from campaign generation | Yes (`/campaigns/generate`) | Yes | Yes | **ACTIVE — not ML** |

---

### 18.2 Model Artifact Status

```
REQUIRED + PRESENT:
  backend/models/model.pkl  (GradientBoosting, 134 KB)
  NOTE: This artifact was built with an older sklearn version.
        Loading with the current sklearn raises:
        ModuleNotFoundError: No module named 'sklearn.ensemble._gb_losses'
        It must be retrained with the current environment.

REQUIRED + MISSING:
  Segmentation model artifact — K-Means is trained in-memory on demand.
  No artifact is persisted between runs. Each API call to /segmentation
  re-trains from scratch. save_model() exists in code but is never called.

OPTIONAL + MISSING:
  Recommendation engine matrix — built in-memory; no persistence.
  AdvancedClusteringModel artifacts — never trained.
  DeepLearningModel artifacts — never trained; TF unavailable.

NOT ACTUALLY USED:
  All classes in advanced_models.py (AdvancedClusteringModel,
  DeepLearningModel, EnsembleModel, AutoMLModel)
```

---

### 18.3 Training Dataset

**Source:** `backend/data/customer_insights.db` — fully synthetic, generated by `backend/scripts/generate_standalone_data.py`.

| Property | Value |
|---|---|
| Customers | 1,000 |
| Transactions | 14,881 |
| Categories | 8 (Food & Dining, Shopping, Entertainment, Transportation, Health & Wellness, Technology, Travel, Education) |
| Merchants | ~70 (realistic brand names per category) |
| Transaction amounts | Lognormal distribution per category; range $5–$5,000 |
| Date range | Up to 2 years back from generation date |
| Seasonal multipliers | Applied (0.8×–1.3× by month) |
| Missing values in features | 31 (in `spending_std` — customers with a single transaction have no std) |
| Synthetic data | Yes — all data is programmatically generated. No real customer data. |

**Data generation method:** `random.choice`, `np.random.lognormal`, no fixed global seed → dataset is **not reproducible** between runs unless the same random state is set.

---

### 18.4 Features Used Per Model

#### GradientBoosting Classifier

Input features are **transaction-level** (one row per transaction):

| Feature | How derived |
|---|---|
| `amount` | Raw transaction amount |
| `cat_count` | Count of transactions for this customer × category combination |
| `recency_days` | Days from this transaction's date to the dataset max date |

**Target:** `1` if `amount > customer_median_amount`, else `0`. Binary. The median is computed per customer across their full history and merged back, which introduces **potential data leakage** (the median uses all transactions including the test set).

**Train/test split:** 80/20 stratified, `random_state=42`.  
**Preprocessing:** No scaling applied.  
**Cross-validation:** None.  
**Hyperparameter tuning:** None (all defaults).

#### K-Means Customer Segmentation

Input features are **customer-level aggregates** (one row per customer):

| Feature | How derived |
|---|---|
| `total_spent` | Sum of all transaction amounts |
| `avg_transaction_amount` | Mean of transaction amounts |
| `transaction_count` | Number of transactions |
| `avg_monthly_spend` | total_spent / (lifetime_days / 30) |
| `transaction_frequency` | transaction_count / lifetime_days |
| `recency_days` | Days since last transaction (from current date) |
| `unique_merchants` | Count of distinct merchants |

**Preprocessing:** Log1p transform on `total_spent`, `avg_transaction_amount`, `avg_monthly_spend`; then StandardScaler; missing values filled with column median.

#### Collaborative Filtering Recommendations

**Input matrix:** customer × category (1,000 × 8). Values are row-normalised sums of transaction amounts per category.  
**Similarity:** Cosine similarity computed over the full 1,000 × 1,000 matrix.  
**Neighbors:** Top 10 most similar customers.  
**Output:** Top-N weighted category scores.

---

### 18.5 Current Measured Performance

#### GradientBoosting Classifier

Metrics measured live on the current database with the default `GradientBoostingClassifier` (all sklearn defaults), 80/20 stratified split, `random_state=42`.

| Metric | Value |
|---|---|
| Accuracy | **0.9154 (91.5%)** |
| ROC-AUC | **0.9741 (97.4%)** |
| Precision | **0.9107 (91.1%)** |
| Recall | **0.9145 (91.4%)** |
| F1 Score | **0.9126 (91.3%)** |

**Confusion matrix (test set, n=2,977):**
```
              Predicted 0  Predicted 1
Actual 0         1,410          129
Actual 1           123        1,315
```

**Target class distribution (full dataset, n=14,881):**
```
Class 0 (amount <= customer median): 7,694 (51.7%)
Class 1 (amount >  customer median): 7,187 (48.3%)
```
→ Near-balanced target; no class imbalance issue.

**Feature importances:**
```
amount:       99.25%
cat_count:     0.37%
recency_days:  0.38%
```
> **CRITICAL FINDING:** The model is almost entirely driven by `amount` alone. `cat_count` and `recency_days` contribute negligible signal. The task — predicting whether a transaction amount exceeds the per-customer median — is near-trivially solved once `amount` is included as an input feature, because `amount` *is* what defines the target. This results in inflated metrics that do not reflect genuine predictive power over meaningful business outcomes.

#### K-Means Customer Segmentation — Clustering Quality

Measured on 1,000 customers × 7 features, StandardScaler + log1p preprocessing:

| k | Silhouette | Calinski-Harabasz | Davies-Bouldin | Inertia | Cluster sizes |
|---|---|---|---|---|---|
| 2 | **0.3621** | 492.9 | 1.1517 | 4685.7 | 585, 415 |
| 3 | 0.3100 | 398.2 | 1.2274 | 3891.5 | 487, 119, 394 |
| 4 | 0.3180 | 394.1 | 0.9909 | 3200.5 | 492, 119, 387, 2 |
| 5 | 0.3156 | 377.1 | 0.9611 | 2782.2 | 103, 467, 2, 50, 378 |
| 6 | 0.2873 | 378.0 | 0.9612 | 2412.8 | 181, 378, 366, 2, 48, 25 |
| 7 | 0.3150 | 389.6 | 0.9379 | 2087.0 | 387, 340, 22, 2, 75, 136, 38 |
| 8 | 0.2607 | 390.8 | 1.0130 | 1862.9 | 194, 151, 278, 2, 23, 35, 55, 262 |

**Best silhouette score:** k=2 at **0.3621**.  
**Best Davies-Bouldin:** k=7 at **0.9379** (lower is better).

> **FINDING:** Silhouette scores in the range 0.26–0.36 indicate **fair to weak cluster separation**. The clusters are not well-separated in the current feature space. Critically, k=4+ produces a cluster of size 2 — essentially singleton/outlier clusters — indicating the data does not naturally form more than 2–3 meaningful groups. The API default of `n_clusters=5` produces two singleton clusters of size 2.

**Segment naming method:** Rule-based post-hoc labeling based on cluster centroid quantile comparisons (e.g., if avg spend > 75th percentile → "High-Value"). Segment names are NOT learned; they are assigned by thresholding centroid values after clustering.

#### Collaborative Filtering Recommendations

**Matrix shape:** 1,000 customers × 8 categories.  
**Sparsity:** ~24% zeros (because with only 8 categories and many transactions, most customers appear in most categories).

**Evaluation:** NOT MEASURED. No precision@K, recall@K, MAP@K, NDCG, or any ranking metric is implemented anywhere in the codebase. There is no held-out test set for recommendation quality.

**Cold-start behavior:** If a new customer has no transaction history, they will not appear in the customer-item matrix and will raise a `ValueError`. There is no cold-start handling.

---

### 18.6 Data Quality Assessment

| Property | Finding |
|---|---|
| Missing values | 31 rows in `spending_std` (customers with a single transaction) |
| Duplicate transactions | Deduplicated during generation; 0 duplicates in DB |
| Invalid amounts | All amounts > 0; lognormal bounded per category |
| Future transactions | Not present; filtered by generator |
| Class imbalance (GBM) | Near-balanced (51.7% / 48.3%) |
| Cluster imbalance | Severe at k≥4 (singleton clusters of size 2 appear) |
| Recommendation sparsity | Low (only 8 categories; most customers have all) |
| Reproducibility | No global random seed in generator; each run produces a different dataset |
| Feature correlation | `total_spent`, `avg_monthly_spend`, `avg_transaction_amount`, `transaction_frequency` are all derived from the same transaction amounts — highly correlated |
| Real-world validity | **None.** All data is programmatically generated using `random.choice` and `np.random.lognormal`. Category preferences, spending behaviors, and merchant choices are all random — no realistic behavioral patterns or customer personas exist. |

> **KNOWN LIMITATION:** Because the dataset is fully synthetic and behaviorally random, ML results cannot be extrapolated to production. Models will need to be retrained on real customer transaction data before any business conclusions can be drawn.

---

### 18.7 Model → Application Wiring

```
[CONNECTED]
Raw Transactions (SQLite)
  ↓
DataPreprocessor.create_customer_features()
  ↓
CustomerSegmentation.perform_segmentation()  [K-Means]
  ↓ segment_id, segment_name
DatabaseManager.insert_dataframe("customer_segments")
  ↓
FastAPI GET /segments  →  Streamlit Dashboard (segment views)
  ↓
RulesEngine.evaluate_customer_for_campaigns()  [Rule-based, not ML]
  ↓
CampaignGenerator.generate_personalized_campaigns()
  ↓
FastAPI POST /campaigns/generate  →  Streamlit Dashboard (campaigns tab)

[CONNECTED but artifact incompatible]
Raw Transactions (SQLite)
  ↓
training.load_data() + build_features()
  ↓
GradientBoostingClassifier.fit()
  ↓
backend/models/model.pkl  (must be retrained; current artifact is sklearn-version-incompatible)
  ↓
model_server.py  POST /predict  (returns score + label)
  ↓
gateway.py  POST /predict  (proxies to model server)

[NOT WIRED — orphaned implementation]
RecommendationEngine.create_customer_item_matrix()
RecommendationEngine.calculate_customer_similarity()
RecommendationEngine.generate_category_recommendations()
  → No API endpoint calls these methods
  → No Streamlit dashboard page calls these methods
  → Not used by campaign engine

[DEAD CODE — no callers anywhere]
AdvancedClusteringModel, DeepLearningModel, EnsembleModel, AutoMLModel
  → Defined in advanced_models.py
  → No imports of these classes exist anywhere outside the file itself
```

---

### 18.8 Current ML Weaknesses

The following weaknesses were identified directly from the codebase and measured data:

1. **Synthetic training data only.** All ML models are trained on programmatically generated data with no behavioral structure. Real-world performance is entirely unknown.

2. **Leaky GBM target.** The binary target is `amount > per_customer_median_amount`. The median is computed over the full dataset (including test rows) before splitting, creating data leakage. The 97.4% AUC is partially inflated.

3. **Near-trivial GBM task.** `amount` alone accounts for 99.25% of feature importance. The model essentially learns `amount > threshold` — a task with trivially high accuracy that has no obvious business utility.

4. **No meaningful GBM business target.** Predicting whether a transaction is above the customer's own median is not a business-relevant prediction (e.g., churn, next-purchase, LTV, campaign response).

5. **No cross-validation.** Neither the GBM model nor the clustering uses cross-validation. Single-split evaluation with one random seed.

6. **No hyperparameter optimisation.** All models use sklearn defaults.

7. **Weak clustering separation.** Best silhouette score is 0.36 (k=2). At k=5 (API default), singleton clusters of size 2 appear, indicating the data does not support meaningful multi-segment grouping.

8. **Segment names are rule-based, not data-driven.** Cluster labels (e.g., "High-Value-Frequent-Active") are assigned post-hoc by comparing centroid values to dataset quantiles. The ML step (KMeans) groups customers; the naming is deterministic business logic.

9. **Recommendation engine is completely disconnected.** `RecommendationEngine` is fully implemented but has zero callers in the API, dashboard, or campaign engine. Its output is never consumed.

10. **No recommendation evaluation.** No ranking metrics (Precision@K, Recall@K, NDCG, MAP) are computed anywhere.

11. **Recommendation cold-start unhandled.** New customers with no transactions cause a `ValueError`.

12. **Sparse category space makes CF trivially dense.** With only 8 categories and ~15 transactions per customer, almost all customers appear in all categories. Cosine similarity between customers will be very high across the board, making recommendations low-quality and undifferentiated.

13. **Model artifact is sklearn-version-incompatible.** The existing `model.pkl` was serialised with an older sklearn version containing `sklearn.ensemble._gb_losses` (removed in newer sklearn). The artifact must be deleted and regenerated.

14. **No model versioning or experiment tracking.** `model_utils.py` has a `save_model()` helper with timestamp filenames, but it is never called. No MLflow, DVC, or equivalent is used.

15. **No feature monitoring or drift detection.** There is no mechanism to detect when customer behavior shifts and the model needs retraining.

16. **No prediction monitoring.** The ML model server logs request counts via Prometheus but does not log prediction distributions or monitor for prediction drift.

17. **Segmentation model not persisted.** `save_model()` exists in `CustomerSegmentation` but is never called. Each `/segmentation` API call re-trains KMeans from scratch.

18. **No A/B evaluation on campaigns.** `campaign_orchestrator.py` implements A/B test variant creation, but there is no mechanism to measure actual conversion outcomes or feed results back.

19. **Highly correlated input features.** `total_spent`, `avg_monthly_spend`, and `avg_transaction_amount` are all derived from the same transaction amounts. This redundancy weakens clustering structure.

20. **No online learning.** All models are batch-trained only.

---

## 19. Future ML & Intelligence Roadmap

> **FUTURE IMPLEMENTATION** — None of the following features exist in the current codebase. They are recommendations only.

---

### Priority 1 — Accuracy & Data Quality

1. **Replace synthetic data with real transaction data.** The single highest-impact improvement. Connect to an actual POS system, payment processor, or CRM dataset. Without real data, no ML metric is meaningful.

2. **Fix GBM target formulation.** Replace the per-customer-median target with a business-relevant binary label, such as:
   - Customer churn within next 60 days (recency-based)
   - Campaign response (clicked/converted)
   - High-value transaction indicator (>$200 absolute threshold, not relative)

3. **Fix data leakage.** Compute per-customer median strictly on the training set; apply the same thresholds to the test set without re-computing.

4. **Add temporal validation.** Use time-based train/test splits rather than random splits. Train on transactions up to date T; evaluate on transactions after T. This reflects real deployment scenarios.

5. **Add cross-validation.** Use at least 5-fold stratified cross-validation for GBM evaluation. Report mean ± std of all metrics.

6. **Add hyperparameter tuning.** Use `RandomizedSearchCV` or `Optuna` for GBM hyperparameters (`n_estimators`, `max_depth`, `learning_rate`, `subsample`).

7. **Improve feature engineering.** Add behaviorally meaningful features:
   - Category entropy (diversity of spending)
   - Weekend vs. weekday spending ratio
   - Average time between transactions
   - Share of wallet by category
   - Trend features (spending acceleration/deceleration)

8. **Handle correlated features.** Apply PCA or feature selection (e.g., variance-based, mutual information) to reduce redundancy among spend-derived features before clustering.

---

### Priority 2 — Segmentation

1. **Persist the segmentation model artifact.** Call `save_model()` after each training run. Load the existing model for predictions rather than re-training on every API call.

2. **Evaluate cluster stability.** Run KMeans with multiple random seeds and measure label agreement (Adjusted Rand Index) across runs. Unstable segments should not be used for campaign targeting.

3. **Validate optimal k against business criteria.** The statistically optimal k (highest silhouette) may not produce business-useful segments. Cross-validate segment utility by checking whether campaigns targeted at different segments produce different response rates.

4. **Add segment drift monitoring.** Schedule monthly reclustering and measure how many customers change segments (Adjusted Rand Index vs. previous month). Alert when drift exceeds threshold.

5. **Improve cluster naming.** Move from hardcoded quantile thresholds to percentile-relative labeling that adapts as the customer base changes.

6. **Consider HDBSCAN.** HDBSCAN handles non-spherical clusters and automatically determines the number of clusters, avoiding the manual k selection problem.

---

### Priority 3 — Recommendations

1. **Wire the recommendation engine.** The existing `RecommendationEngine` implementation is complete. Add API endpoints (`GET /customers/{id}/recommendations`) and expose results in the Streamlit dashboard.

2. **Add recommendation evaluation.** Implement offline evaluation using a hold-out time window: train on transactions up to month T, evaluate recommendations on month T+1. Compute Precision@K, Recall@K, NDCG@K.

3. **Handle cold-start.** For new customers with fewer than N transactions, fall back to:
   - Global category popularity rankings
   - Segment-level average preferences (once the customer has a segment assignment)

4. **Expand beyond categories to merchants.** The `generate_merchant_recommendations` method already exists but is not evaluated. Connect merchant recommendations to the campaign engine (cross-sell to specific merchants).

5. **Add temporal decay weighting.** Recent transactions should have higher weight in the customer-item matrix than older ones. Use exponential decay by transaction date.

6. **Hybrid collaborative + content-based filtering.** Augment cosine similarity with content features (category affinity, average amount, time-of-day preference) to improve recommendation quality especially for sparse users.

---

### Priority 4 — Campaign Intelligence

1. **Replace rule-based eligibility with ML-based propensity scores.** Instead of hard thresholds (`total_spent >= $1000`), train a logistic regression or GBM model predicting the probability that a customer will respond to a given campaign type, using historical campaign outcome data.

2. **Add expected-uplift estimation.** For each (customer, campaign_type) pair, estimate the incremental revenue uplift vs. sending no campaign. Rank campaigns by uplift rather than priority score.

3. **Close the campaign feedback loop.** Persist campaign outcome data (sent, opened, converted, revenue generated) and use it as training signal for propensity models.

4. **A/B test evaluation.** Implement statistical significance testing (chi-squared or t-test) on A/B campaign variants. Currently variants are created but outcomes are never measured.

5. **Personalise discount amounts.** Currently discounts are fixed per campaign type. Train a regression model predicting the minimum discount needed to convert a given customer, avoiding over-discounting high-propensity customers.

---

### Priority 5 — Production ML

1. **Fix model artifact compatibility.** Delete `backend/models/model.pkl` and regenerate it with the current sklearn version. Add a version tag inside the artifact (sklearn version, training date, metrics).

2. **Add MLflow experiment tracking.** Log training runs with `mlflow.log_params()`, `mlflow.log_metrics()`, and `mlflow.sklearn.log_model()`. This enables model comparison, reproducibility, and rollback.

3. **Add model versioning.** The `ModelUtils.save_model()` helper produces timestamped filenames. Extend this to include a metadata JSON with sklearn version, feature list, metrics, and training dataset hash.

4. **Add automated retraining triggers.** Extend the Celery `retrain_model` task to check whether the current model's metrics have degraded below a threshold (e.g., AUC < 0.85 on recent data) before triggering retraining.

5. **Add feature monitoring.** Log monthly distributions of all input features (mean, std, percentiles). Alert when distributions shift significantly from training-time distributions (PSI > 0.2).

6. **Add prediction monitoring.** Log the model's predicted probability distribution from the model server. Alert when the distribution shifts (e.g., mean score drops from 0.5 to 0.3).

7. **Add SHAP explainability.** Integrate `shap` to generate per-prediction feature attribution values, enabling business-readable explanations of campaign eligibility decisions.

---

## 20. Proposed Differentiating Feature: Customer Behavioral Simulation Engine

> **FUTURE IMPLEMENTATION ONLY.** This feature does not exist in the current codebase.

---

### Feature Name
**Customer Behavioral Simulation Engine (CBSE)** — "What happens to this customer if we do nothing vs. send campaign X vs. send campaign Y?"

---

### Problem It Solves

CICOP currently generates campaigns based on static eligibility rules and a priority score. It has no mechanism to answer the question: **"What is the predicted business outcome if we take a specific action for this customer?"**

Campaign managers today must guess which campaign to send, at what discount, and through which channel — with no forward-looking prediction of the customer's likely behavior. There is also no ability to simulate future customer journeys under different intervention scenarios.

---

### Why It Is Different

Most customer analytics dashboards tell you **what happened** (KPI views) or **who to target** (segmentation). A small number tell you **what is likely to happen** (churn prediction). CBSE goes further: it lets business users ask **"what if?"** questions about individual customers or entire segments, using the platform's own ML and rules layers as the simulation engine.

This is different from a simple propensity model because:
- It simulates multiple competing actions simultaneously, not a single prediction
- It leverages all three existing CICOP layers: segmentation, collaborative filtering, and the rules engine
- It produces actionable, interpretable business outcomes (expected revenue, expected churn reduction) not just probability scores
- It enables human-in-the-loop decision making without replacing automated campaign generation

---

### How It Builds on Existing CICOP Components

| Existing component | Role in CBSE |
|---|---|
| `CustomerSegmentation` | Determines which behavioral cohort the customer belongs to |
| `RecommendationEngine` | Predicts which categories/merchants the customer is most likely to engage with next |
| `RulesEngine` | Defines the candidate action space (which campaigns are eligible) |
| `CampaignGenerator` | Generates specific campaign configurations for each simulated action |
| `GradientBoostingClassifier` (retrained) | Predicts transaction likelihood and expected amount under each action scenario |
| `DatabaseManager` | Provides the historical behavioral baseline for the simulation |

---

### Required Data

- Historical campaign outcome data (sent → opened → converted → revenue) — **currently missing; requires collection**
- Customer transaction history — **already present**
- Segment assignments — **already present**
- Campaign configurations — **already present**

---

### ML Components Required (Future)

- A **campaign response propensity model** — logistic regression or GBM trained on historical campaign outcomes, predicting P(conversion | customer_features, campaign_type, discount)
- A **revenue uplift estimator** — regression model predicting expected incremental revenue above baseline for each (customer, campaign) pair
- A **churn risk model** — binary classifier predicting P(no transaction in next 60 days) used as the baseline "do nothing" scenario
- The existing **recommendation engine** to constrain which product categories appear in the simulation

---

### Inputs

- `customer_id` (or `segment_id` for bulk simulation)
- A list of candidate actions: e.g., `[loyalty_reward@15%, win_back@25%, no_campaign]`
- Simulation horizon: e.g., 30 days, 60 days

---

### Outputs

For each candidate action, for each customer:

```
Action: loyalty_reward (15% discount, email channel)
  Expected conversion probability:   0.73
  Expected incremental revenue:       $47.20
  Expected cost (discount):           $14.25
  Expected net uplift:                $32.95
  Recommended channel:                email (optimal timing: Tue 09:00)
  Confidence interval (90%):          $18 – $52

Action: no_campaign (baseline)
  Expected next purchase within 30d:  0.61
  Expected revenue (organic):         $29.10
  Churn risk:                         12%

Recommended action:  loyalty_reward
Reason:              Highest expected net uplift ($32.95) vs. baseline
```

---

### Example User Workflow

1. Business user opens **Simulation** tab in the Streamlit dashboard
2. Selects a customer or segment
3. Selects candidate campaigns from a dropdown (populated from `CampaignGenerator`)
4. Selects a simulation horizon (30 / 60 / 90 days)
5. Clicks **Run Simulation**
6. Dashboard displays a comparison table of predicted outcomes per action
7. User selects the best action and clicks **Deploy Campaign** — which calls `POST /campaigns/generate` with the chosen configuration

---

### Business Value

- Eliminates guesswork from campaign targeting decisions
- Prevents over-discounting (if a customer would convert at 10%, don't offer 25%)
- Reduces campaign cost while maintaining or improving revenue outcomes
- Provides measurable ROI predictions before any budget is spent
- Builds institutional knowledge about which campaign types work for which customer profiles

---

### How Success Would Be Measured

- Uplift in campaign conversion rate vs. rule-only baseline (A/B test)
- Reduction in average discount per converted customer
- Increase in net revenue per campaign sent
- Correlation between predicted uplift and actual uplift (model calibration)

---

### Implementation Complexity

**High.** Requires:
1. Campaign outcome tracking infrastructure (new DB table + API endpoint)
2. Training propensity and uplift models on real campaign outcome data
3. Simulation engine connecting all existing ML components
4. Streamlit simulation UI

Estimated: 3–4 sprints after campaign outcome data collection is in place.

---

### Why It Could Become CICOP's Signature Capability

Every competitor analytics platform can show KPIs and segment customers. Very few go beyond segmentation to provide **decision-level simulation** grounded in the customer's own behavioral data. CBSE would transform CICOP from a reporting tool into an **active decision support system** — positioning it as a competitive differentiator in the CRM and marketing intelligence space.

---

## 21. ML Audit Summary

### ML Models Found

| # | Model | Status |
|---|---|---|
| 1 | GradientBoosting Classifier | Active (artifact needs retraining) |
| 2 | K-Means Customer Segmentation | Active (no artifact persistence) |
| 3 | Collaborative Filtering (Cosine Similarity) | Implemented but not wired |
| 4 | AdvancedClusteringModel (ensemble) | Dead code |
| 5 | DeepLearningModel (TF/MLP) | Dead code (TF not installed) |
| 6 | EnsembleModel (VotingClassifier) | Dead code |
| 7 | AutoMLModel (GridSearchCV) | Dead code |

### Model Artifacts

```
Required and present:
  backend/models/model.pkl  — INCOMPATIBLE (must retrain)

Required and missing:
  Segmentation artifact — never persisted

Not applicable (in-memory only):
  Recommendation engine matrix — computed per request

Dead code (never trained):
  AdvancedClusteringModel, DeepLearningModel, EnsembleModel, AutoMLModel
```

### Training Data

| Model | Dataset | Rows | Features | Target |
|---|---|---|---|---|
| GradientBoosting | SQLite transactions (synthetic) | 14,881 transaction rows | amount, cat_count, recency_days | Binary: amount > per-customer median |
| K-Means | SQLite transactions aggregated to customers | 1,000 customer rows | 7 behavioral features | None (unsupervised) |
| Collaborative Filtering | SQLite transactions as customer×category matrix | 1,000 × 8 | Row-normalised spend per category | None (similarity-based) |

### Current Measured Performance

| Model | Metric | Value |
|---|---|---|
| GradientBoosting | Accuracy | 91.5% |
| GradientBoosting | ROC-AUC | 97.4% |
| GradientBoosting | Precision | 91.1% |
| GradientBoosting | Recall | 91.4% |
| GradientBoosting | F1 | 91.3% |
| K-Means (k=2) | Silhouette | 0.3621 |
| K-Means (k=2) | Calinski-Harabasz | 492.9 |
| K-Means (k=2) | Davies-Bouldin | 1.1517 |
| K-Means (k=5, API default) | Silhouette | 0.3156 |
| Collaborative Filtering | Any ranking metric | NOT MEASURED |

> High GBM metrics are inflated by a near-trivial target definition and data leakage. They do not represent production-ready performance.

### ML Health Assessment

| Dimension | Rating | Notes |
|---|---|---|
| Data Quality | Poor | 100% synthetic, no behavioral structure, not reproducible |
| Model Coverage | Partial | GBM served; segmentation active; recommendations orphaned |
| Evaluation Quality | Poor | Leaky GBM target; no CV; no recommendation evaluation; clustering marginally separated |
| Production Readiness | Not ready | Artifact incompatible; no versioning; no monitoring; no feedback loop |
| Main ML Risk | No real data | All metrics are measures of synthetic data performance only |

### Top 5 Future Improvements by Value

1. **Replace synthetic data with real transaction data** — without this, no other improvement produces valid results
2. **Fix GBM target** — redefine to predict a genuine business outcome (churn, campaign response, LTV)
3. **Wire the recommendation engine** — fully implemented but currently producing zero value
4. **Add temporal cross-validation** — eliminates leakage and provides realistic performance estimates
5. **Implement campaign outcome tracking** — enables propensity models and closes the feedback loop

### Signature Differentiating Feature

**Customer Behavioral Simulation Engine (CBSE)** — a what-if simulation layer that predicts the business outcome of each possible campaign action for each customer, enabling data-driven campaign selection rather than rule-based targeting. Builds directly on existing segmentation, recommendations, and campaign generation components. No comparable feature exists in CICOP today.

---

## 22. Data Strategy & Readiness

> **Audit Date:** 2026-08-17  
> **Target Document:** Root `TECHNICAL.md`  
> **Status:** Exhaustive Data Audit, Canonical Data Model Specification, and Production Data Strategy.

---

### 22.1 Current Data Architecture & Foundation Audit

The data layer of CICOP comprises 4 SQLite/PostgreSQL database tables, a synthetic data generator script, a data preprocessor, a data loader, and feature engineering utilities.

#### Database Tables & Actual Attributes

```
customers (1,000 rows)
├── customer_id (TEXT, PK)          [e.g., CUST_000001]
├── first_name (TEXT)               [e.g., John]
├── last_name (TEXT)                [e.g., Smith]
├── email (TEXT)                    [e.g., customer1@example.com]
├── registration_date (DATE)        [e.g., 2024-09-15]
├── age (INTEGER)                   [Range: 18 - 80]
├── gender (TEXT)                   [Male, Female, Other]
└── location (TEXT)                 [e.g., New York, NY]

transactions (14,881 rows)
├── transaction_id (TEXT, PK)       [e.g., TXN_00000001]
├── customer_id (TEXT, FK)          [References customers.customer_id]
├── transaction_date (DATE)         [e.g., 2024-09-18]
├── amount (REAL)                   [Range: $5.00 - $5,000.00]
├── category (TEXT)                 [8 unique categories]
├── subcategory (TEXT)              [40 subcategories]
├── merchant (TEXT)                 [~70 merchant brands]
└── payment_method (TEXT)           [6 payment methods]

customer_segments (1,000 rows)
├── customer_id (TEXT, PK, FK)      [References customers.customer_id]
├── segment_id (INTEGER)            [0 to 4]
├── segment_name (TEXT)             [e.g., High-Value-Frequent-Active]
└── last_updated (DATE)             [Timestamp of last clustering run]

campaigns (2,002 rows)
├── campaign_id (TEXT, PK)          [e.g., CAMP_000001]
├── customer_id (TEXT, FK)          [References customers.customer_id]
├── campaign_type (TEXT)            [loyalty_reward, win_back, cross_sell, etc.]
├── offer_description (TEXT)        [Human-readable offer string]
├── discount_amount (REAL)          [Discount percentage or amount]
├── created_date (DATE)             [e.g., 2026-07-20]
└── status (TEXT)                   [active, sent, expired]
```

#### Key Empirical Characteristics

- **Time Coverage:** 2-year window (approx. August 2024 to August 2026).
- **Categorical Fields:** 8 spending categories, 40 subcategories, 70 merchants, 6 payment methods, 3 genders, 5 segment names, 5 campaign types, 3 campaign statuses.
- **Numerical Fields:** Transaction amount, customer age, discount amount, segment_id.
- **Derived Fields (Engineered in `DataPreprocessor`):** `total_spent`, `avg_transaction_amount`, `transaction_count`, `spending_std`, `first_transaction`, `last_transaction`, `primary_category`, `unique_merchants`, `customer_lifetime_days`, `avg_monthly_spend`, `transaction_frequency`, `recency_days`.
- **Missing Values:** 31 null values in `spending_std` for customers with exactly 1 transaction (std computation requires N ≥ 2).
- **Duplicates & Outliers:** 0 duplicate primary keys; amounts follow lognormal truncation.
- **Reproducibility:** **Low.** `generate_standalone_data.py` uses `random.randint` and `random.choice` without setting a deterministic global random seed (`random.seed()` or `np.random.seed()`). Running data generation produces a different SQLite instance every time.

---

### 22.2 Synthetic Data Audit & Behavioral Realism

The dataset is generated programmatically via `backend/scripts/generate_standalone_data.py`.

#### Generation Methodology & Mathematical Distributions
1. **Customers:** Uniform random sampling of first names, last names, cities (30), states (20), ages ($U(18, 80)$), genders, and registration dates ($U(1, 730)$ days ago).
2. **Transactions:** Number of transactions per customer sampled as $U(1, 30)$ (mean 15). Category is chosen uniformly at random (`random.choice(categories)`). Transaction amount is generated via lognormal distribution:
   $$\mu = \log\left(\frac{\text{min\_amount} + \text{max\_amount}}{2}\right), \quad \sigma = 0.5$$
   bounded by min and max thresholds per category.
3. **Seasonality:** Multipliers applied post-generation based on month (e.g., December = 1.3×, January = 0.8×).
4. **Segments:** Rule-based quantile split on `total_spent`, `avg_monthly_spend`, and `transaction_count`.

#### Behavioral Realism Findings

> **Can the current dataset be used to demonstrate realistic production ML performance?**  
> **NO.** The dataset cannot evaluate production ML performance for the following specific reasons:

1. **Lack of Behavioral Persona Structure:** Categories are chosen uniformly at random per transaction (`random.choice`). A single customer will buy `Food & Dining`, `Technology`, `Health & Wellness`, and `Travel` with equal probability. There are no customer personas (e.g., tech enthusiasts, budget grocers, frequent travelers).
2. **Zero Cross-Category Correlation:** A customer spending $2,000 on `Technology` is no more likely to buy high-end `Shopping` items than a customer spending $20 on `Fast Food`.
3. **Absence of Customer Inertia / Habit:** Transaction dates are sampled uniformly between customer registration date and present day. There are no inter-purchase arrival patterns (e.g., weekly grocery trips, monthly subscriptions).
4. **No Churn or Inactivity Dynamics:** Inactive customers do not exist naturally due to non-renewal or dissatisfaction; low-recency customers are merely an artifact of random date uniform sampling.
5. **No Campaign Outcome Data:** The `campaigns` table stores generated campaign proposals (`active`, `sent`, `expired`), but **zero campaign response data** (open rates, click-throughs, conversions, redemptions, post-campaign revenue).
6. **Trivial Machine Learning Targets:** Because features and targets are derived from independent random draws, supervised models either learn trivial identity definitions (e.g., `amount > customer_median`) or fit pure random noise.

---

### 22.3 Data Quality Audit

| Dimension | Standard | Audit Findings | Status |
|---|---|---|---|
| **Completeness** | All critical fields populated | 31 missing values in `spending_std` (single-transaction customers). Campaign outcomes, interaction timestamps, product SKUs, and channel delivery metrics are 100% missing. | **PARTIAL** |
| **Accuracy** | Values adhere to domain constraints | All transaction amounts > 0. Customer ages between 18 and 80. Dates bounded within 2 years. | **PASS** |
| **Consistency** | Referential integrity & schema agreement | All `transactions.customer_id` reference valid `customers.customer_id`. Foreign key constraints declared in DDL. Category names standardized in Title Case. | **PASS** |
| **Uniqueness** | Zero duplicate entities | Primary keys (`customer_id`, `transaction_id`, `campaign_id`) have 0 duplicate values. No duplicate customer emails. | **PASS** |
| **Timeliness** | Chronological ordering & recency | Transaction dates span up to present day. However, recency is calculated dynamically against execution time rather than fixed evaluation snapshots. | **WARNING** |
| **Reproducibility**| Deterministic dataset generation | Generator lacks fixed random seeds (`random.seed(42)` / `np.random.seed(42)`). Re-running generation yields non-identical data tables. | **FAIL** |

---

### 22.4 CICOP Canonical Data Model (Target Specification)

This specification defines the normalized data schema required for CICOP to operate as a production-grade Customer Intelligence & Campaign Orchestration Platform.

#### 1. Entity: `Customer` (Core Profile)

| Field | Type | Required | Purpose | ML Usage | Status |
|---|---|---|---|---|---|
| `customer_id` | String (UUID/Text) | Yes | Primary Key | Entity key | **Exists** |
| `first_name` | String | No | Personalization | NLP / PII (exclude from ML) | **Exists** |
| `last_name` | String | No | Personalization | PII (exclude from ML) | **Exists** |
| `email` | String | Yes | Identity / Channel | Identity matching | **Exists** |
| `registration_date` | Date/Timestamp | Yes | Tenure calculation | Lifetime / Cohort feature | **Exists** |
| `age` | Integer | No | Demographic | Demographic feature | **Exists** |
| `gender` | String | No | Demographic | Demographic feature | **Exists** |
| `location` | String | No | Geographic | Geo-clustering / Spatial feature | **Exists** |
| `status` | String | Yes | Lifecycle State | Target / Lifecycle filtering | **Missing** |

#### 2. Entity: `Transaction` (Financial Interactions)

| Field | Type | Required | Purpose | ML Usage | Status |
|---|---|---|---|---|---|
| `transaction_id` | String | Yes | Primary Key | Event ID | **Exists** |
| `customer_id` | String | Yes | Foreign Key | Grouping key | **Exists** |
| `transaction_date` | Timestamp | Yes | Time Series | Temporal features / Recency | **Exists** (Date only) |
| `amount` | Decimal(10,2) | Yes | Revenue | Monetary features / LTV target | **Exists** |
| `category_id` | String | Yes | Hierarchy | Category affinity / Embedding | **Exists** (Text category) |
| `subcategory_id` | String | No | Hierarchy | Sub-category affinity | **Exists** (Text subcategory) |
| `merchant_id` | String | No | Partner tracking | Merchant affinity / Recommendations | **Exists** (Text merchant) |
| `payment_method` | String | No | Channel tracking | Behavioral preference feature | **Exists** |
| `discount_applied` | Decimal(10,2) | No | Margin calculation | Sensitivity / Promotion elasticity | **Missing** |
| `channel` | String | No | Store vs Web vs App | Channel preference feature | **Missing** |

#### 3. Entity: `Product` / `Catalog` (Item Metadata)

| Field | Type | Required | Purpose | ML Usage | Status |
|---|---|---|---|---|---|
| `product_id` | String | Yes | Primary Key | Item CF / Recommender candidate | **Missing** |
| `product_name` | String | Yes | Display | Search / Recommendation label | **Missing** |
| `category_id` | String | Yes | Taxonomy | Category-level recommendations | **Needs Impr.** (Text string) |
| `unit_price` | Decimal(10,2) | Yes | Pricing | Price sensitivity feature | **Missing** |
| `cost_price` | Decimal(10,2) | No | Margin calculation | Campaign profit optimization | **Missing** |

#### 4. Entity: `Campaign` (Marketing Strategy Definition)

| Field | Type | Required | Purpose | ML Usage | Status |
|---|---|---|---|---|---|
| `campaign_id` | String | Yes | Primary Key | Campaign ID | **Exists** |
| `campaign_name` | String | Yes | Name | Metadata | **Needs Impr.** |
| `campaign_type` | String | Yes | Classification | Propensity model feature | **Exists** |
| `target_segment` | String | No | Rule filter | Segment targeting feature | **Exists** (In code) |
| `channel` | String | Yes | Delivery channel | Channel selection model | **Missing** (Hardcoded) |
| `offer_type` | String | Yes | Discount type | Offer elasticity model | **Needs Impr.** |
| `offer_value` | Decimal(10,2) | Yes | Discount value | Cost & uplift model feature | **Exists** (`discount_amount`) |
| `min_purchase` | Decimal(10,2) | No | Condition | Constraint evaluation | **Missing in DB schema** |
| `valid_from` | Timestamp | Yes | Schedule | Temporal boundary | **Missing** |
| `valid_to` | Timestamp | Yes | Expiration | Expiration boundary | **Missing** |

#### 5. Entity: `Campaign_Dispatch` (Sent Interventions)

| Field | Type | Required | Purpose | ML Usage | Status |
|---|---|---|---|---|---|
| `dispatch_id` | String | Yes | Primary Key | Event ID | **Missing** |
| `campaign_id` | String | Yes | Foreign Key | Intervention key | **Missing** |
| `customer_id` | String | Yes | Foreign Key | Customer key | **Missing** |
| `dispatch_timestamp`| Timestamp | Yes | Time sent | Treatment time for uplift | **Missing** |
| `channel_used` | String | Yes | Execution channel | Channel performance feature | **Missing** |
| `variant` | String | Yes | A/B testing | Treatment vs Control flag | **Missing** |

#### 6. Entity: `Campaign_Outcome` (Conversion & Attribution)

| Field | Type | Required | Purpose | ML Usage | Status |
|---|---|---|---|---|---|
| `outcome_id` | String | Yes | Primary Key | Outcome event ID | **Missing** |
| `dispatch_id` | String | Yes | Foreign Key | Attribution link | **Missing** |
| `customer_id` | String | Yes | Foreign Key | Customer key | **Missing** |
| `campaign_id` | String | Yes | Foreign Key | Campaign key | **Missing** |
| `opened` | Boolean | Yes | Email/Push open | Conversion pipeline metric | **Missing** |
| `clicked` | Boolean | Yes | Link engagement | Engagement target | **Missing** |
| `converted` | Boolean | Yes | Purchase made | **Propensity / Uplift Target** | **Missing** |
| `conversion_timestamp`| Timestamp| No | Conversion time | Latency to conversion | **Missing** |
| `attributed_revenue` | Decimal(10,2)| No | Direct revenue | Revenue uplift target | **Missing** |
| `campaign_cost` | Decimal(10,2)| Yes | Expense | Net ROI / Uplift optimization | **Missing** |

#### 7. Entity: `Customer_Event` (Behavioral Telemetry)

| Field | Type | Required | Purpose | ML Usage | Status |
|---|---|---|---|---|---|
| `event_id` | String | Yes | Primary Key | Telemetry ID | **Missing** |
| `customer_id` | String | Yes | Foreign Key | Behavioral tracking | **Missing** |
| `event_type` | String | Yes | Action type | Real-time intent features | **Missing** |
| `event_timestamp` | Timestamp | Yes | Time of action | Real-time triggers / Recency | **Missing** |
| `properties_json` | JSON/Text | No | Event metadata | Contextual ML features | **Missing** |

---

### 22.5 Customer 360 Data Requirements

A genuine Customer 360 view requires segregating raw attributes, aggregated historical behaviors, engineered feature vectors, engagement history, and ML-predicted metrics.

```
                  ┌─────────────────────────────────────────┐
                  │          CUSTOMER 360 PROFILE           │
                  └────────────────────┬────────────────────┘
                                       │
     ┌──────────────────┬──────────────┼──────────────┬──────────────────┐
     │                  │              │              │                  │
┌────▼──────────┐ ┌─────▼────────┐ ┌───▼──────────┐ ┌─▼─────────────┐ ┌──▼──────────────┐
│ Raw Profile   │ │ Transaction  │ │ Behavioral   │ │ Engagement    │ │ Derived ML     │
│ & Identity    │ │ History      │ │ Features     │ │ & Touchpoints │ │ Intelligence   │
└───────────────┘ └──────────────┘ └──────────────┘ └───────────────┘ └────────────────┘
```

1. **Raw Profile & Identity:** `customer_id`, `first_name`, `last_name`, `email`, `registration_date`, `age`, `gender`, `location`, `status`.
2. **Transaction History Aggregates:** Total spend ($), transaction count ($N$), average order value (AOV), lifetime span (days), min/max transaction date.
3. **Engineered Behavioral Features:** Recency (days), frequency (tx/day), monetary (RFM), category spend vectors, merchant diversity, spending trend slope, spending std, weekend ratio, primary category.
4. **Engagement & Touchpoint Tracking:** Total campaigns dispatched, open rate (%), click-through rate (%), conversion rate (%), preferred channel, last campaign date, total discount redeemed ($).
5. **Derived ML Intelligence (Predictions):**
   - Cluster Segment ID & Name (Unsupervised)
   - Churn Risk Score ($P(\text{churn}) \in [0, 1]$)
   - Next-30-Day Purchase Probability ($P(\text{purchase}) \in [0, 1]$)
   - Campaign Propensity Score per Type ($P(\text{convert} \mid \text{campaign}_k)$)
   - Predicted Customer Lifetime Value (365-day CLV $)
   - Recommended Product Categories / Merchants (Top-$K$)
   - Net Campaign Uplift ($E[\Delta \text{Revenue}]$)

---

### 22.6 Mapping Data → Future ML Objectives

| ML Objective | Required Data | Currently Available | Missing Data | Minimum History | Evaluation Protocol |
|---|---|---|---|---|---|
| **1. Customer Segmentation** | RFM features, category percentages, merchant diversity, tenure | `total_spent`, `avg_amount`, `tx_count`, `recency`, `unique_merchants` | Category spend %, channel split, return rate | 3 months | Silhouette score, Davies-Bouldin, Segment stability over time |
| **2. Churn Prediction** | Historical transaction time series, inactivity windows | Historical transactions | Binary churn labels, explicit churn events, activity logs | 6 months | Temporal train/test split, ROC-AUC, Precision-Recall @ K |
| **3. Purchase Prediction** | Inter-purchase arrival times, category search, spend trend | Dates, amounts | Product SKUs, web/app events, cart additions | 3 months | ROC-AUC, Log-Loss, Top-K Hit Rate |
| **4. Campaign Response** | Campaign dispatch logs, open/click/conversion events, offer details | Sent campaigns (no outcomes) | Open, click, conversion timestamps, redemption flags | 6 months (with campaigns) | ROC-AUC, PR-AUC, Cumulative Gain Chart |
| **5. Product Recommendation** | Customer $\times$ Product transaction matrix, item metadata | Customer $\times$ Category matrix (8 categories) | Item/SKU level transactions, product catalog, ratings | 3 months | Precision@K, Recall@K, MAP@K, NDCG@K |
| **6. Customer Lifetime Value** | Periodic spend aggregations, cohort tenure, margin data | Lifetime aggregate spend | Margin/cost data, historical cohort snapshots | 12 months | RMSE, MAE, R-squared, Decile Rank Accuracy |
| **7. Campaign Uplift** | Randomized treatment/control campaign dispatches + outcomes | None | Explicit Control Group ($T_0$), Treatment Group ($T_1$), Revenue outcomes | 6 months (A/B data) | Qini Curve, Qini Score, Uplift @ Decile |
| **8. Offer Optimization** | Discount elasticity history, min purchase compliance, profit margins | Discount amounts | Cost of goods sold (COGS), redemption vs non-redemption revenue | 6 months | Profit Maximization Metric, Counterfactual Eval |
| **9. Behavioral Simulation (CBSE)**| Complete Customer 360 + Propensity models + Uplift models | Features & static rules | Full campaign interaction telemetry & response labels | 12 months | Backtesting against historical campaign experiments |

---

### 22.7 Future ML Target Formulations

To eliminate data leakage and support real-world intelligence, future ML targets must be formulated with strict observation and prediction windows:

#### Target 1: Customer Churn ($Y_{\text{churn}}$)
$$\text{Observation Window } [T_0, T_1] \implies \text{Feature Extraction}$$
$$\text{Prediction Window } (T_1, T_1 + 60 \text{ days}] \implies \text{Label Assignment}$$
- **Label Definition:** $Y = 1$ if no transaction occurs between $T_1 + 1$ and $T_1 + 60$; $Y = 0$ otherwise.
- **Leakage Prevention:** Features extracted strictly from transactions $\le T_1$.
- **Evaluation:** Temporal split (train on Q1-Q3, validate on Q4). Metric: PR-AUC, Recall@Top-20%.

#### Target 2: Campaign Conversion Propensity ($Y_{\text{conv}}$)
- **Label Definition:** $Y = 1$ if customer completed a qualifying purchase within campaign validity window ($T_{\text{dispatch}} + \text{validity\_days}$) following dispatch; $Y = 0$ if dispatched but unredeemed.
- **Required Data:** `campaign_outcomes` table with explicit `converted` boolean.
- **Evaluation:** Stratified temporal split by campaign launch date. Metric: ROC-AUC, Calibration Curve (Brier Score).

#### Target 3: Next 30-Day Spending Volume ($Y_{\text{spend}}$)
- **Label Definition:** Continuous value $Y = \sum_{t=T_1+1}^{T_1+30} \text{amount}_t$.
- **Leakage Prevention:** Zero transaction data from $> T_1$ included in predictors.
- **Evaluation:** Time-series rolling window cross-validation. Metric: MAE, WAPE (Weighted Absolute Percentage Error).

#### Target 4: Incremental Campaign Uplift ($\Delta Y$)
- **Label Definition:** $\Delta Y = E[Y \mid \text{Treatment}] - E[Y \mid \text{Control}]$.
- **Required Data:** Randomized A/B dispatch tags (`variant='treatment'` vs `variant='control'`).
- **Evaluation:** Qini curve AUC and Uplift@Decile 1-3.

---

### 22.8 Minimum Data Requirements Matrix

| ML Objective | Min Customers | Min Transactions | Min Time Horizon | Min Positive Cases | Min Campaign Records | Current CICOP Sufficiency |
|---|---|---|---|---|---|---|
| **Customer Segmentation** | 500 | 5,000 | 3 months | N/A (Unsupervised) | N/A | **Sufficient in volume**, insufficient in behavioral variation |
| **Churn Prediction** | 2,000 | 20,000 | 6 months | 300 churned | N/A | **Insufficient** (No realistic churn dynamics) |
| **Purchase Prediction** | 1,000 | 15,000 | 3 months | 1,000 purchases | N/A | **Sufficient in volume**, insufficient in SKU detail |
| **Campaign Response** | 1,000 | 10,000 | 6 months | 200 conversions | 2,000 dispatches | **Insufficient** (0 conversion records) |
| **Product Recommendation**| 1,000 | 25,000 | 3 months | 500 multi-buy | N/A | **Insufficient** (Only 8 coarse categories) |
| **Customer Lifetime Value**| 2,500 | 30,000 | 12 months | N/A (Regression) | N/A | **Insufficient** (2-year uniform draw lacks tenure depth) |
| **Campaign Uplift / CBSE**| 5,000 | 50,000 | 12 months | 500 conversions | 5,000 dispatches | **Insufficient** (No A/B outcome records) |

---

### 22.9 Real-World Data Integration Architecture

CICOP should implement a **Normalized Data Ingestion Interface** to abstract external data sources (CSV, PostgreSQL, REST APIs, POS exports) into canonical CICOP entities.

```
┌────────────────────────────────────────────────────────────────────────┐
│                          EXTERNAL DATA SOURCES                         │
├─────────────┬─────────────┬─────────────┬──────────────┬───────────────┤
│ CSV / Excel │  REST APIs  │ POS Systems │ Ecommerce DB │ Payment Gate. │
└──────┬──────┴──────┬──────┴──────┬──────┴──────┬───────┴──────┬────────┘
       │             │             │             │              │
       ▼             ▼             ▼             ▼              ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   CICOP DATA ADAPTER & INGESTION LAYER                 │
│  - Schema Validation (Pydantic / Great Expectations)                   │
│  - Type Casting & Timestamp Normalization                              │
│  - Entity Resolution & Customer Deduplication                          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      CICOP CANONICAL DATA MODEL                        │
│   (customers, transactions, products, campaigns, outcomes, events)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                FEATURE STORE & ML PIPELINE / RULES ENGINE               │
└────────────────────────────────────────────────────────────────────────┘
```

---

### 22.10 Public Development Dataset Criteria

To replace synthetic data with a realistic open dataset for development and benchmarking, candidate datasets must satisfy the following criteria:

1. **Transaction Granularity:** Individual transaction line items with explicit timestamps (date + time).
2. **Customer Tracking:** Persistent masked `customer_id` across multiple purchases over at least 9–12 months.
3. **Product Taxonomy:** At least 50–500 distinct product SKUs or detailed subcategories.
4. **Behavioral Diversity:** Natural Pareto spend distribution (top 20% customers generating ~80% revenue).
5. **Candidate Datasets:**
   - **Online Retail II (UCI ML Repository):** 1M+ transactions, 5,000+ customers, 2-year temporal span, real SKU descriptions.
   - **Instacart Market Basket Analysis:** Real customer purchase repeat patterns across thousands of products.
   - **Taobao / E-commerce User Behavior Dataset:** User interaction telemetry (view, cart, buy).

---

### 22.11 Dataset Transition Plan

```
┌──────────────────────────┐
│ STAGE 1: SYNTHETIC DATA  │ Current state: Functional code verification, API & UI testing.
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ STAGE 2: PUBLIC DATASET  │ Ingest Online Retail II into Canonical Schema. Benchmark real
└────────────┬─────────────┘ K-Means clustering, Recommendation Engine, and Churn ML models.
             │
             ▼
┌──────────────────────────┐
│ STAGE 3: CANONICAL SCHEMA│ Enforce strict DB migration with campaign outcome telemetry tables.
└────────────┬─────────────┘ Validate Feature Store & temporal splitting.
             │
             ▼
┌──────────────────────────┐
│ STAGE 4: PRODUCTION SMB  │ Connect real client POS / E-commerce databases via Adapters.
└──────────────────────────┘ Enable full Campaign Uplift & Simulation Engine.
```

---

### 22.12 Data Leakage & Temporal Validation Strategy

To guarantee production reliability, all future ML training pipelines in CICOP must enforce **Strict Temporal Splits**:

```
                       DATASET TEMPORAL TIMELINE
├─────────────────────────────────────────┼───────────────┼───────────────┤
│          HISTORICAL TRAINING            │  VALIDATION   │     TEST      │
│           (e.g., Months 1 - 9)          │ (Month 10-11) │  (Month 12)   │
└─────────────────────────────────────────┴───────────────┴───────────────┘
                                          ▲               ▲
                                    Split Date 1    Split Date 2
```

1. **No Future Information Leakage:** Features at split date $T_{\text{split}}$ must strictly use data $\le T_{\text{split}}$.
2. **No Target Contamination:** Aggregates (e.g., median spend, mean tx amount) used in target definitions must be computed solely on the training fold.
3. **Campaign Window Isolation:** Campaign propensity models must enforce a minimum 14-day attribution window following dispatch before assigning label state.

---

### 22.13 Campaign Intelligence Data Requirements

Advanced campaign capabilities (Propensity, Uplift, A/B Testing, Offer Optimization, and Simulation) require logging the complete lifecycle of every campaign dispatch.

#### Required Event Telemetry Schema (`campaign_outcomes` / `campaign_dispatches`)

```sql
CREATE TABLE IF NOT EXISTS campaign_dispatches (
    dispatch_id TEXT PRIMARY KEY,
    campaign_id TEXT NOT NULL,
    customer_id TEXT NOT NULL,
    variant TEXT NOT NULL,          -- 'treatment_a', 'treatment_b', 'control'
    channel TEXT NOT NULL,          -- 'email', 'sms', 'push', 'in_app'
    dispatch_timestamp TIMESTAMP NOT NULL,
    offer_discount_pct REAL,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS campaign_outcomes (
    outcome_id TEXT PRIMARY KEY,
    dispatch_id TEXT NOT NULL,
    opened INTEGER DEFAULT 0,       -- 0 or 1
    clicked INTEGER DEFAULT 0,      -- 0 or 1
    converted INTEGER DEFAULT 0,    -- 0 or 1
    conversion_timestamp TIMESTAMP,
    attributed_revenue REAL DEFAULT 0.0,
    campaign_cost REAL DEFAULT 0.0,
    FOREIGN KEY (dispatch_id) REFERENCES campaign_dispatches(dispatch_id)
);
```

#### Analytical Utility Matrix

- **Response Propensity Models:** Requires `dispatches` $\to$ `converted` (1/0).
- **A/B Testing:** Requires `variant` column ('treatment' vs 'control') and `attributed_revenue`.
- **ROI Computation:** Requires `attributed_revenue` minus `campaign_cost`.
- **Uplift Modeling:** Requires comparing conversion rate of `treatment` group vs `control` group.
- **Simulation Engine (CBSE):** Requires historical conversion rates across different `offer_discount_pct` values.

---

### 22.14 Data Feedback Loop Architecture

```
                  ┌────────────────────────────────────────┐
                  │          CUSTOMER TRANSACTIONS         │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │              CUSTOMER 360              │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │         ML MODELS & RULES ENGINE       │
                  │   (Segmentation, Propensity, Uplift)   │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │          CAMPAIGN DISPATCH             │
                  │     (Treatment vs Control Split)       │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │           CUSTOMER RESPONSE            │
                  │   (Open → Click → Convert → Spend)    │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │       CAMPAIGN OUTCOME LOGGING         │
                  │  (campaign_dispatches & outcomes)      │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │     FEATURE STORE & RETRAINING RUN     │
                  │  (Closed Feedback Loop for Future ML)  │
                  └────────────────────────────────────────┘
```

---

### 22.15 Prioritized Data Work Plan

#### P0 — Critical (Foundational Prerequisites)
1. **Fix Random Seed in Data Generator:** Add `random.seed(42)` and `np.random.seed(42)` in `generate_standalone_data.py` to ensure reproducible dev runs. (Effort: 5 mins).
2. **Create Campaign Outcome Schema:** Add DDL for `campaign_dispatches` and `campaign_outcomes` to `DatabaseManager`. (Effort: 1 hour).
3. **Ingest Public Benchmark Dataset:** Migrate from pure synthetic data to the **Online Retail II** dataset for realistic ML evaluation. (Effort: 1 day).

#### P1 — High Value (ML & Intelligence Enhancements)
1. **Persist Segmentation Artifacts:** Update `CustomerSegmentation` to save and load `segmentation_model.pkl` instead of re-clustering on every API call. (Effort: 2 hours).
2. **Wire Recommendation Engine to API:** Expose `RecommendationEngine` via FastAPI endpoints `/ml/recommend` and Streamlit UI. (Effort: 4 hours).
3. **Implement Temporal Validation:** Refactor `training.py` to split train/test sets chronologically by `transaction_date`. (Effort: 2 hours).

#### P2 — Later Maturity (Production Expansion)
1. **Build Normalized Data Adapter Interface:** Support CSV/POS/PostgreSQL external ingestion pipeline. (Effort: 3 days).
2. **Implement Feature Store & Drift Monitoring:** Track feature distribution shifts (PSI) and prediction drift. (Effort: 1 week).
3. **Implement Customer Behavioral Simulation Engine (CBSE):** Build what-if uplift simulation once 6+ months of campaign response data exists. (Effort: 2 weeks).

---

### 22.16 Candidate Dataset Forensic Comparison

> **Audit Date:** 2026-08-17  
> **Location Inspected:** `backend/training/` (`online_retail_ii/`, `instacart/`, `taobao/`)  
> **Status:** Analysis-only forensic evaluation. Zero files modified, zero database schemas altered, zero ML models trained.

---

#### 1. Dataset Inventory

| Dataset | File Name(s) | Size on Disk | Files | Row Count | Column Count | Key Data Types | Dev Machine Feasibility |
|---|---|---|---|---|---|---|---|
| **Online Retail II** | `online_retail_II.xlsx` | 45.62 MB | 1 (2 sheets) | **1,067,371** | 8 | `object`, `int64`, `float64`, `datetime64[ns]` | **EXCELLENT** — Fits entirely in RAM (~150 MB Pandas memory). |
| **Instacart** | `orders.csv`, `order_products__prior.csv`, `order_products__train.csv`, `products.csv`, `aisles.csv`, `departments.csv` | 714.23 MB | 6 | **37,290,486** (total across all 6 files) | 2–7 per file | `int64`, `float64`, `object` | **GOOD** — Requires chunked joins or selective column loading (~1.5 GB Pandas memory). |
| **Taobao User Behavior** | `UserBehavior.csv` | 3.67 GB | 1 | **100,150,807** | 5 | `int64`, `object` | **HEAVY** — Must use chunked streaming (`chunksize=5,000,000`) or DuckDB/Polars (~4–6 GB RAM if unchunked). |

---

#### 2. Customer Structure Analysis

| Metric / Dimension | Online Retail II | Instacart | Taobao User Behavior |
|---|---|---|---|
| **Unique Customer Count** | **5,942** (with non-null IDs) | **206,209** | **987,994** (~1 Million) |
| **Customer Identifier** | `Customer ID` (Float/Text) | `user_id` (Integer) | `user_id` (Integer) |
| **ID Persistence Across Orders** | **Yes** (Tracks multi-year repeat purchases) | **Yes** (Tracks consecutive order numbers 1 to 100) | **Yes** (Tracks clickstream events per user) |
| **Orders per Customer (Mean)** | 7.55 orders | 16.59 orders | 101.37 interactions |
| **Orders per Customer (Median)** | 4.0 orders | 10.0 orders | 46.0 interactions |
| **Orders per Customer (Max)** | 510 orders | 100 orders (capped by dataset) | 13,000+ interactions |
| **One-Time Customers (1 order)**| **1,461 (24.59%)** | **0 (0.00%)** (Instacart filtered for $\ge 4$ orders) | 1,204 (0.12%) |
| **Repeat Customers (>1 order)** | **4,481 (75.41%)** | **206,209 (100.00%)** | 986,790 (99.88%) |
| **Customer History Duration** | **Mean: 275.4 days**, Max: 738 days (~2 years) | Relative intervals (`days_since_prior_order` 0–30) | **9 days** (Nov 25 – Dec 03, 2017) |
| **Longitudinal Modeling Capability** | **STRONG** — Supports multi-year RFM, churn, LTV cohorts | **MEDIUM** — Supports reorder frequency & sequential baskets | **WEAK** — Only 9 days of interaction weblogs |

---

#### 3. Transaction / Order Structure (Attribute Availability)

| Entity / Field | Online Retail II | Instacart | Taobao User Behavior |
|---|---|---|---|
| `transaction_id` / `order_id` | **DIRECTLY AVAILABLE** (`Invoice`) | **DIRECTLY AVAILABLE** (`order_id`) | **NOT AVAILABLE** (Event log only) |
| `customer_id` / `user_id` | **DIRECTLY AVAILABLE** (`Customer ID`) | **DIRECTLY AVAILABLE** (`user_id`) | **DIRECTLY AVAILABLE** (`user_id`) |
| `product_id` / `item_id` | **DIRECTLY AVAILABLE** (`StockCode`) | **DIRECTLY AVAILABLE** (`product_id`) | **DIRECTLY AVAILABLE** (`item_id`) |
| `quantity` | **DIRECTLY AVAILABLE** (`Quantity`) | **DERIVABLE** (Count of items in basket) | **NOT AVAILABLE** |
| `unit_price` / `amount` | **DIRECTLY AVAILABLE** (`Price`) | **NOT AVAILABLE** (0 pricing data) | **NOT AVAILABLE** (0 pricing data) |
| `total_revenue` | **DERIVABLE** (`Quantity * Price`) | **NOT AVAILABLE** | **NOT AVAILABLE** |
| `transaction_timestamp` | **DIRECTLY AVAILABLE** (`InvoiceDate`) | **DERIVABLE** (Relative DOW + Hour + Interval) | **DIRECTLY AVAILABLE** (`timestamp`) |
| `category` | **DERIVABLE** (Parsed from `Description`) | **DIRECTLY AVAILABLE** (`department` / `aisle`) | **DIRECTLY AVAILABLE** (`category_id` - ID only) |
| `merchant` / `store` | **NOT AVAILABLE** (Single retailer) | **NOT AVAILABLE** | **NOT AVAILABLE** |
| `geographic_location` | **DIRECTLY AVAILABLE** (`Country`, 43 countries) | **NOT AVAILABLE** | **NOT AVAILABLE** |
| `returns` / `cancellations` | **DIRECTLY AVAILABLE** (`Invoice` starts with 'C') | **NOT AVAILABLE** | **NOT AVAILABLE** |
| `reorder_indicator` | **DERIVABLE** (Product re-purchases) | **DIRECTLY AVAILABLE** (`reordered` boolean) | **DERIVABLE** (Repeated buys) |

---

#### 4. Temporal Analysis

```
Online Retail II Timeline (738 Calendar Days)
├─────────────────────────────────────────────────────────────────────────┤
2009-12-01 07:45                                          2011-12-09 12:50

Instacart Timeline (Relative Sequence)
[Order 1] ──(days_since_prior)──► [Order 2] ──...──► [Order N (max 100)]

Taobao User Behavior Timeline (9 Calendar Days)
├─────────┤
2017-11-25 to 2017-12-03
```

- **Online Retail II:** Spans **December 1, 2009 to December 9, 2011** (738 calendar days). Has exact datetime stamps (`2009-12-01 07:45:00`). Fully supports **Temporal Train $\to$ Validation $\to$ Test splits** (e.g., Train: 2009-12 to 2011-05; Validation: 2011-06 to 2011-09; Test: 2011-10 to 2011-12).
- **Instacart:** **NO calendar timestamps.** Provides relative `order_dow` (0–6), `order_hour_of_day` (0–23), and `days_since_prior_order` (0–30 days). Cannot perform real-world temporal split by year/month.
- **Taobao:** Spans **November 25, 2017 to December 03, 2017** (only 9 calendar days of dense user clickstreams). Too short for seasonality, churn, or long-term LTV modeling.

---

#### 5. Data Quality Audit

| Data Quality Metric | Online Retail II | Instacart | Taobao User Behavior |
|---|---|---|---|
| **Missing Values** | `Customer ID`: 243,007 rows (22.77% guest checkouts); `Description`: 4,382 rows (0.41%). All other fields 100% complete. | `days_since_prior_order`: 206,209 rows (first order of each user). 0 missing product/user IDs. | **0 missing values** across all 100.15M rows. |
| **Exact Duplicate Rows** | 34,335 duplicate rows (3.21%). Easily deduplicated. | **0 duplicate rows**. | **0 duplicate rows**. |
| **Negative Quantities / Returns**| 22,950 rows with negative quantity (cancellations/returns, marked with 'C' invoice). Reflects real retail returns. | None. | None. |
| **Zero / Negative Prices** | 5 negative prices; 6,202 zero prices (free samples/adjustments). | N/A (No price column). | N/A (No price column). |
| **Invalid Timestamps** | 0 invalid datetimes. | N/A (Relative integer fields). | Out-of-bounds telemetry noise (0.01% corrupted UNIX timestamps outside Nov 2017). |
| **Orphaned Foreign Keys** | 0 orphaned StockCodes. Non-null Customer IDs match clean customer entity tables. | 0 orphaned `product_id`, `aisle_id`, `department_id`. | 0 orphaned IDs. |
| **Distribution Skew** | Top 10% customers generate ~68% revenue (Pareto spend). | Top 20% products account for ~74% reorders (`Banana`, `Bag of Organic Bananas`). | 89.58% `pv` (view), 5.52% `cart`, 2.88% `fav`, 2.01% `buy` (Heavy click-to-buy dropoff). |

---

#### 6. Behavioral Realism Assessment

- **Online Retail II:** **🟢 NATURALLY OCCURRING.** Contains real commercial wholesale and retail orders from a UK-based online gift store. Exhibits natural Pareto spending concentrations, seasonal holiday spikes (November/December volume increases), organic repeat order intervals, and genuine product return/cancellation behaviors.
- **Instacart:** **🟢 NATURALLY OCCURRING.** Contains authentic grocery reorder behavior from 206k real Instacart shoppers. Exhibits strong organic basket composition (e.g., fresh produce reordered every 7 days, pantry items every 21 days). However, financial behavior (spend/prices) is missing.
- **Taobao User Behavior:** **🟡 PARTIALLY STRUCTURED.** Represents real mobile e-commerce clickstream telemetry, but 89.6% of events are passive page views (`pv`), and only 2.0% are actual purchases (`buy`). Highly dense over 9 days, but lacks long-term customer lifecycle structure.

---

#### 7. Product & Category Richness

| Aspect | Online Retail II | Instacart | Taobao User Behavior |
|---|---|---|---|
| **Unique Products (SKUs)** | **5,305** (`StockCode`) | **49,688** (`product_name`) | **4,162,024** (`item_id`) |
| **Product Descriptions** | Real English text (e.g., `WHITE HANGING HEART T-LIGHT HOLDER`) | Real English text (e.g., `Organic Whole Milk`) | Integer IDs only (e.g., `2364718`) |
| **Unique Categories** | Derivable from item descriptions | **134 Aisles**, **21 Departments** | **9,439 Category IDs** |
| **Taxonomy Structure** | Flat SKU $\to$ Description | 3-tier: Product $\to$ Aisle $\to$ Department | 2-tier: Item ID $\to$ Category ID |
| **Recommendation Engine Potential**| **EXCELLENT** for item-item & category CF with monetary weighting | **EXCELLENT** for market basket analysis & basket completion | **GOOD** for sequential session-based next-item prediction |

---

#### 8. Customer 360 Compatibility Matrix

| Customer 360 Attribute | Online Retail II | Instacart | Taobao User Behavior |
|---|---|---|---|
| **Raw Profile & Identity** | 🟡 `customer_id`, `Country` (No age/gender) | 🔴 `user_id` only | 🔴 `user_id` only |
| **Transaction History** | 🟢 Total spend ($), Tx count, AOV, Lifetime span | 🟡 Order count, Basket size (No $ spend) | 🔴 Action count only (No $ spend) |
| **Behavioral Features** | 🟢 RFM metrics, Recency, Frequency, Country preference | 🟢 Reorder ratio, Aisle/Dept affinity, DOW/Hour habits | 🟡 Click-to-buy ratio, Category view frequency |
| **Engagement Tracking** | 🔴 No campaign history | 🔴 No campaign history | 🔴 No campaign history |
| **Derived Intelligence** | 🟢 Segmentation, Churn, LTV, Recommendations | 🟡 Reorder Prediction, Basket CF | 🟡 Next-Item Click Prediction |

---

#### 9. ML Objective Compatibility Matrix

| ML Objective | Online Retail II | Instacart | Taobao User Behavior |
|---|---|---|---|
| **1. Customer Segmentation** | 🟢 **STRONG** (RFM + Category + Country clustering) | 🟡 **PARTIAL** (Basket frequency & department preference) | 🔴 **WEAK** (Short 9-day clickstream behavior) |
| **2. Churn Prediction** | 🟢 **STRONG** (60-day post-observation inactivity label) | 🔴 **MISSING** (No calendar timestamps to define inactivity) | 🔴 **MISSING** (9-day window too short for churn) |
| **3. Next Purchase Prediction** | 🟢 **STRONG** (Predict purchase date & total spend) | 🟢 **STRONG** (Predict next basket items & reorder time) | 🟡 **PARTIAL** (Predict next clicked item in session) |
| **4. Recommendation System** | 🟢 **STRONG** (Monetary-weighted Collaborative Filtering) | 🟢 **STRONG** (Market Basket & Reorder Item CF) | 🟡 **PARTIAL** (Sequential Item-Item CF with integer IDs) |
| **5. Customer Lifetime Value (CLV)**| 🟢 **STRONG** (Regression on 365-day cumulative spend) | 🔴 **MISSING** (Zero price/revenue data) | 🔴 **MISSING** (Zero price/revenue data) |
| **6. Campaign Response Propensity**| 🔴 **MISSING** (No campaign logs) | 🔴 **MISSING** (No campaign logs) | 🔴 **MISSING** (No campaign logs) |
| **7. Campaign Uplift Modeling** | 🔴 **MISSING** (No treatment/control) | 🔴 **MISSING** (No treatment/control) | 🔴 **MISSING** (No treatment/control) |
| **8. Behavioral Simulation (CBSE)**| 🟡 **PARTIAL** (Base behavioral simulator without campaign feedback) | 🔴 **MISSING** (No monetary value to simulate ROI) | 🔴 **MISSING** (No financial outcomes to simulate) |

---

#### 10. Campaign Data Gap Investigation

> **CRITICAL FINDING:**  
> **None of the three candidate datasets (Online Retail II, Instacart, Taobao) contain marketing campaign logs, offer dispatches, discount redemptions, A/B treatment/control tags, or campaign response outcomes.**

- **Why this gap exists:** All three are organic e-commerce transaction/clickstream datasets collected without marketing intervention tracking.
- **Impact on CICOP:** None of these public datasets can independently train CICOP's future campaign-response propensity models or uplift models out of the box.
- **Bridge Strategy for CICOP:**
  1. Use **Online Retail II** as the primary data foundation for **Customer 360, Behavioral Segmentation, Churn Prediction, Product Recommendations, and LTV Modeling**.
  2. Implement the `campaign_dispatches` and `campaign_outcomes` telemetry schema (documented in §22.13) within CICOP's database layer.
  3. Overlay synthetic campaign dispatches and responses onto the real Online Retail II customer base during development, establishing the closed feedback loop required for propensity and uplift models.

---

#### 11. Canonical Schema Mapping

##### Mapping for `Online Retail II` $\to$ CICOP Canonical Schema

| Source Field (`online_retail_II.xlsx`) | CICOP Canonical Entity.Field | Data Transformation Required |
|---|---|---|
| `Customer ID` | `customers.customer_id` | Cast float to string `CUST_{int}`; filter nulls for strict customer ML. |
| `InvoiceDate` (min per customer) | `customers.registration_date` | Aggregated minimum datetime per customer. |
| `Country` | `customers.location` | Direct string assignment. |
| `Invoice` | `transactions.transaction_id` | Direct string assignment (`TXN_{Invoice}`). |
| `Customer ID` | `transactions.customer_id` | Foreign Key reference. |
| `InvoiceDate` | `transactions.transaction_date` | Direct datetime assignment. |
| `Quantity * Price` | `transactions.amount` | Calculated product total in USD/GBP. |
| `Description` | `transactions.category` | Rule-based string parsing to derive top-level category. |
| `StockCode` | `products.product_id` | Direct item ID assignment. |
| `Description` | `products.product_name` | Direct product title assignment. |
| `Price` | `products.unit_price` | Direct unit price assignment. |
| *None* | `campaigns.*` | *Unpopulated — Managed by CICOP Rules Engine / Campaign Generator.* |
| *None* | `campaign_outcomes.*` | *Unpopulated — Managed by CICOP Event Telemetry.* |

---

#### 12. Dataset-Specific Strengths & Weaknesses

##### Online Retail II
- **Strengths:** Contains real monetary spend ($), exact quantities, unit prices, calendar timestamps spanning 2 full years, 5,942 repeat customers, return/cancellation indicators, and real product titles.
- **Weaknesses:** 22.77% of rows lack `Customer ID` (guest checkouts); single-store retailer (no multi-merchant diversity); lacks customer age/gender demographics.
- **Best CICOP Use:** **PRIMARY PLATFORM DATASET** — Powers Customer 360, RFM Segmentation, Churn Prediction, LTV Regression, and Monetary Collaborative Filtering.

##### Instacart
- **Strengths:** Massive scale (206k users, 3.4M orders, 32M item purchases); 100% repeat customers ($\ge 4$ orders); rich 3-tier product taxonomy (49,688 products, 134 aisles, 21 departments).
- **Weaknesses:** **Zero financial data** (no prices, amounts, or revenues); no calendar dates (only relative day/hour/interval); no customer demographics.
- **Best CICOP Use:** **SECONDARY / RESEARCH DATASET** — Benchmark for advanced Market Basket Analysis and Basket Recommendation algorithms.

##### Taobao User Behavior
- **Strengths:** 100M rows of dense multi-behavior clickstream telemetry (`pv`, `cart`, `fav`, `buy`).
- **Weaknesses:** **3.67 GB file size**; no monetary spend; no product names (integer IDs only); **only 9 days of activity**; 89.6% page views vs 2.0% purchases.
- **Best CICOP Use:** **DO NOT USE FOR CICOP CORE** — Incompatible with financial customer intelligence and local development constraints.

---

#### 13. Local Development Machine Feasibility

- **Online Retail II (45.6 MB):** Can be loaded directly into Pandas in memory (< 2 seconds, ~150 MB RAM). Ideal for local rapid iteration, unit testing, andStreamlit dashboard rendering.
- **Instacart (714 MB):** Can be loaded selectively in Pandas or queried using DuckDB without exceeding local RAM limits (~1.5 GB RAM).
- **Taobao (3.67 GB):** Requires chunked processing (`pd.read_csv(..., chunksize=5000000)`) or DuckDB to prevent out-of-memory crashes on 8GB/16GB dev laptops.

---

#### 14. Dataset Weighted Evaluation Matrix

$$\text{Score} = \sum_{i=1}^{9} w_i \cdot s_i \quad (\text{out of 100})$$

| Evaluation Criteria | Weight | Online Retail II | Instacart | Taobao User Behavior |
|---|---|---|---|---|
| **Customer 360 Richness** | 15% | **12 / 15** | 6 / 15 | 4 / 15 |
| **Transaction Quality** | 15% | **14 / 15** | 7 / 15 | 4 / 15 |
| **Behavioral Richness** | 15% | **14 / 15** | 14 / 15 | 10 / 15 |
| **Recommendation Potential** | 15% | **12 / 15** | **15 / 15** | 10 / 15 |
| **Predictive ML Potential** | 15% | **14 / 15** | 10 / 15 | 7 / 15 |
| **Revenue / LTV Potential** | 10% | **10 / 10** | 0 / 10 | 0 / 10 |
| **Temporal Depth** | 5% | **5 / 5** | 2 / 5 | 1 / 5 |
| **Product / Category Richness**| 5% | 4 / 5 | **5 / 5** | 3 / 5 |
| **Data Quality & Usability** | 5% | 4 / 5 | **5 / 5** | 4 / 5 |
| **TOTAL WEIGHTED SCORE** | **100%** | 🏆 **89 / 100** | 🥈 **64 / 100** | 🥉 **43 / 100** |

---

#### 15. Primary Dataset Decision

> ### 🏆 PRIMARY CICOP DEVELOPMENT DATASET: **Online Retail II**

##### Why Online Retail II Wins:
1. **Full Financial Integrity:** It is the **only** candidate dataset containing real transaction prices, quantities, and calculated revenues—enabling real monetary LTV, RFM segmentation, and spend-based predictions.
2. **2-Year Calendar Depth:** Spans 738 calendar days with exact timestamps, allowing defensible **Temporal Train $\to$ Validation $\to$ Test splits** without future-data leakage.
3. **Genuine Customer Repeat Dynamics:** 75.41% repeat customer rate with a mean customer lifespan of 275 days, supporting real churn modeling (inactivity $> 60$ days).
4. **Optimal Local Developer Footprint:** At 45.6 MB, it loads rapidly into Pandas and SQLite on local dev machines while delivering 1.06M transaction rows across 5,942 customers.

##### Secondary / Research Dataset: **Instacart**
Retained strictly as a **secondary research benchmark** for evaluating market basket analysis and product recommendation algorithms (49k products across 134 aisles).

##### Do Not Use: **Taobao User Behavior**
Rejected due to 3.67 GB file footprint, lack of financial metrics, integer-only product IDs, and shallow 9-day time horizon.

---

#### 16. Dataset Combination Decision

> **DECISION: Option A — Use ONE Primary Dataset (Online Retail II) as the canonical database source.**

**Technical Rationale:**  
Do **NOT** attempt to artificially join or merge customer records across Online Retail II and Instacart. Merging synthetic or unrelated customer identities across datasets corrupts behavioral coherence, breaks referential integrity, and creates artificial data leakage. Instacart may be used in isolated offline recommendation notebooks, but **Online Retail II will serve as the single source of truth for the CICOP platform database.**

---

#### 17. Recommended CICOP Data Pipeline Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                        RAW DATA SOURCE LAYER                           │
│             `backend/training/online_retail_ii/online_retail_II.xlsx`  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                    SCHEMA VALIDATION & CLEANING STAGE                  │
│  - Filter missing `Customer ID` rows (22.77% unlogged checkouts)       │
│  - Deduplicate 34,335 duplicate transaction rows                       │
│  - Parse `InvoiceDate` to ISO Timestamps                               │
│  - Separate normal transactions (`Quantity > 0`) from returns (`C*`)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   CANONICAL CICOP DATABASE INGESTION                   │
│   Populate SQLite/Postgres: `customers`, `transactions`, `products`    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                CUSTOMER 360 & FEATURE STORE GENERATION                 │
│  Extract: RFM metrics, category spend vectors, recency, churn state    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                 TEMPORAL SPLIT & ML EXPERIMENTATION                    │
│  Train: [2009-12 to 2011-05]  Val: [2011-06 to 09]  Test: [2011-10 to 12]│
└────────────────────────────────────────────────────────────────────────┘
```

---

#### 18. Anti-Patterns to Avoid

1. ❌ **Do NOT merge unrelated customer IDs** across Online Retail II and Instacart.
2. ❌ **Do NOT use random k-fold train/test splits** on time-series transaction data (causes temporal leakage).
3. ❌ **Do NOT manufacture fake campaign outcome labels** inside the raw Online Retail II dataset.
4. ❌ **Do NOT invent fake customer demographics** (age/gender) unless explicitly marked as synthetic overlays.
5. ❌ **Do NOT overwrite or alter raw files** under `backend/training/`.
6. ❌ **Do NOT load the 3.67 GB Taobao dataset into Pandas memory** without chunking.
7. ❌ **Do NOT claim 99%+ ML accuracy on synthetic targets** as evidence of production readiness.
8. ❌ **Do NOT evaluate recommendation algorithms without temporal hold-out windows.**

---

#### 19. Summary & Actionable Next Steps

- **Dataset Decision:**
  - **PRIMARY:** Online Retail II (`online_retail_II.xlsx`)
  - **SECONDARY (Offline Benchmarking):** Instacart
  - **DO NOT USE:** Taobao User Behavior
- **Why Online Retail II Wins:**
  1. Only dataset with real price ($) and revenue metrics.
  2. 2-year calendar duration (738 days) supporting true temporal validation.
  3. 75.41% repeat customer rate over ~9-month average customer lifespans.
  4. Real English product titles (5,305 SKUs).
  5. Fits perfectly into local machine memory (< 50 MB).
- **Top 5 Missing Attributes to Overlay:**
  1. Campaign dispatch & response outcomes (`campaign_outcomes` schema).
  2. Customer demographic attributes (Age/Gender).
  3. Cost of Goods Sold (COGS) for net profit calculation.
  4. Multi-channel delivery indicators (email/SMS/push).
  5. Web/App telemetry event logs.
- **Best ML Capability From Each Dataset:**
  - **Online Retail II** $\to$ RFM Customer Segmentation, Churn Prediction, LTV Regression.
  - **Instacart** $\to$ Market Basket Analysis & Product Reorder Recommendation.
  - **Taobao** $\to$ Clickstream Session Next-Action Prediction.

> ### 🎯 IMMEDIATE NEXT STEP (Awaiting User Approval):
> **Develop an ingestion script (`backend/scripts/ingest_online_retail.py`) to transform and populate `online_retail_II.xlsx` into CICOP's canonical SQLite database (`backend/data/customer_insights.db`), replacing the synthetic generator.**

---

#### 20. Online Retail II — Data Preparation Pipeline (Hardened v1.1 Semantic Metrics)

**Location:** `backend/training/prepared/online_retail_ii/`

**Pipeline Execution:** 
The semantically hardened reproducible data preparation pipeline (`01_data_preparation.ipynb`) was successfully executed, producing stable canonical parquet files. No modifications were made to the raw `online_retail_II.xlsx` file or the CICOP application code.

**Key Preparation Metrics (from `preparation_report.json`):**
- **Raw Row Count:** 1,067,371
- **Prepared Transaction Count:** 1,033,031
- **Canonical Customer Count:** 5,942 (Identified customers only)
- **Feature Customer Count:** 5,881 (Customers with at least one legitimate purchase)
- **Canonical Product Count:** 5,305
- **Guest Transaction Count:** 235,146
- **Purchase Count:** 1,010,534
- **Return Count:** 3,393
- **Cancellation Count:** 19,104
- **Duplicate Rows Removed:** 34,335
- **Features Constructed:** 21 (Foundational Customer 360 features)
- **Validation Results:** ALL_PASSED

**Output Artifacts Generated:**
- `customers.parquet` (Exclusively identified customers)
- `products.parquet` (Canonical product names)
- `transactions.parquet` (Unified transaction ledger with financial fields)
- `customer_features.parquet` (Foundational Customer 360)
- `preparation_report.json`

**Safeguards & Semantics Implemented:**
- **Financial Correctness:** explicitly calculated `gross_amount` (positive for purchases, 0 for returns), `return_amount` (positive for returns/cancellations, 0 for purchases), and `net_amount = gross_amount - return_amount`. 
- **Guest Segregation:** Null `customer_id` rows remain null and are flagged as `is_guest = True` within the transaction ledger. They are explicitly excluded from `customers.parquet` and Customer 360 aggregations.
- **Transaction Semantics:** Separated logic so cancellations (`Invoice.startswith('C')`) and returns (`Quantity < 0`) are explicitly classified and handled for financial integrity.
- **Foundational Customer 360 (v0.1 Semantics):** 
  - `last_purchase_date` and `first_purchase_date` strictly use `transaction_type == "purchase"`.
  - `purchase_order_count` counts only unique invoices containing purchases.
  - `average_order_value` uses `purchase_order_count` as the denominator.
  - `purchase_frequency` relies strictly on `purchase_order_count` and a purchase-only `customer_lifetime_days`.
  - Added line counts (`purchase_line_count`, `return_line_count`, `cancellation_line_count`) and retained `return_rate` and `cancellation_rate`.
- **Temporal Handling:** Used `max_purchase_date` over identified purchases for relative metric calculations, establishing a solid baseline before formal ML observation window splits are created.

---

#### 21. Temporal ML Dataset Pipeline (Implementation Complete)

**Purpose:** 
To provide a reproducible, leakage-safe, point-in-time dataset simulating historical customer states for training predictive models (next-purchase, LTV, etc.) without exposing future information.

**Source Data:** 
Canonical V1.1 Data Foundation (`customers.parquet`, `transactions.parquet`).

**Temporal Observation Framework:**
- **Observation Frequency:** Monthly.
- **Timestamps:** Observation dates strictly normalized to midnight (00:00:00) to ensure deterministic cutoffs.
- **Lookback Windows:** 30-day, 90-day, and lifetime historical ranges.
- **Lookback Contract:** 90 days is the maximum rolling feature window, NOT a minimum customer-history requirement. Customers enter the temporal panel organically after their first purchase.
- **Prediction Horizons:** 30-day, 60-day, and 90-day future horizons.

**Feature Construction:** 
19 features constructed purely from transactions occurring $\le T$. Includes lifetime RFM metrics (e.g. `FEATURE_recency_days`, `FEATURE_total_gross_purchase_spend`), line-item breakdown (`purchase`, `return`, `cancellation` rates), and discrete rolling windows. 
- *Refinement:* `FEATURE_unique_products` was explicitly tightened to `FEATURE_unique_products_purchased` to prevent returns from artificially inflating behavioral variety.
- *Refinement:* Financials explicitly named to `FEATURE_total_gross_purchase_spend` to resolve semantic ambiguity.

**Target Construction:** 
15 targets constructed strictly from transactions occurring in the window $(T, T + \text{horizon}]$. Targets include binary purchase likelihoods (`TARGET_next_purchase_30d`), future order volumes (`TARGET_future_order_count`), and future financial outcomes (`TARGET_future_net_spend`). 

**Churn Decision:** 
**DEFERRED.** A rigid churn label (e.g., "no purchase in 90 days = churn") was deferred because this dataset mixes wholesale and retail purchasing patterns, creating highly volatile natural inter-purchase intervals. Imposing an arbitrary inactivity threshold without product context would create a misleading target.

**Train/Validation/Test Strategy (Chronological Split):**
- **TRAIN (70%):** $T \in$ [2010-03-31, 2011-02-28] (41,749 rows)
  - Next-purchase 30d/60d/90d rates: `23.4%` / `36.0%` / `44.1%`
- **VALIDATION (15%):** $T \in$ [2011-03-31, 2011-05-31] (14,468 rows)
  - Next-purchase 30d/60d/90d rates: `17.7%` / `28.2%` / `34.4%`
- **TEST (15%):** $T \in$ [2011-06-30, 2011-08-31] (15,430 rows)
  - Next-purchase 30d/60d/90d rates: `17.7%` / `28.6%` / `38.0%`

**Validation Gates & Reproducibility:**
A rigorous final hardening pass was executed.
- **REAL Feature Leakage Gate [PASS]:** 1000 sampled observation windows were explicitly cross-referenced against the raw canonical transactions. Confirmed that 100% of historical transactions strictly possessed `timestamp <= observation_date`.
- **REAL Target Window Gate [PASS]:** 1000 sampled observation windows explicitly verified that future targets fell strictly inside $(T, T + horizon]$, and that `future_net = future_gross - future_return` universally held.
- **REAL Reproducibility Gate [PASS]:** Tested by applying a deterministic hash across the consolidated numerical matrix (Hash: `5950e1471bb11536...`) and demonstrating 100% computational parity upon sampled re-runs.

**Dataset Outputs (`backend/training/prepared/online_retail_ii/temporal/`):**
- `temporal_features.parquet`
- `temporal_targets.parquet`
- `temporal_dataset.parquet`
- `dataset_splits.parquet`
- `temporal_report.json`
- `validation_report.json`

---

### 22. ML Experimentation — 30-Day Next-Purchase Prediction (Phase 1)

**STATUS:** FROZEN (Phase 1 Complete)

**Experiment Objective:**
Determine whether CICOP's Customer 360 combined with temporal feature engineering provides meaningful predictive value for customer next-purchase behavior over a 30-day horizon.

**Target:** `TARGET_next_purchase_30d`

**Selected Model:** `HistGradientBoosting_Tuned`

**Performance (TEST Set):**
- ROC-AUC: 0.8191
- PR-AUC: 0.5627
- Lift @ Top 10%: 3.65×

**Operating Parameters (Empirically Derived):**
- **Classification Threshold:** 0.30 (F1-optimal reference is 0.275)
- **Targeting Budget Default:** Top 10% (Yields ~64.8% precision and 3.65x lift)
- **Propensity Bands:**
  - LOW: < 0.16
  - MODERATE: 0.16 – < 0.27
  - HIGH: 0.27 – < 0.40
  - VERY_HIGH: >= 0.40

**Key Findings:**
- Permutation importance shows behavioral cadence (`recency_days`, `purchase_frequency`, `purchase_order_count_90d`) dominates prediction over raw monetary value.
- Model naturally struggles with "Dormant" cohorts, emphasizing the need for behavioral segmentation before targeting.
- Return-rate features (`FEATURE_return_rate`, `FEATURE_return_line_count`) are mathematically zero for identified customers because in the Online Retail II dataset, identified customer refund behaviors are universally coded as `cancellation` (Invoice prefix 'C'), while `return` (no prefix) applies exclusively to guests. This is an expected semantic behavior of the dataset.

**Experiment Output Location:**
`backend/training/experiments/next_purchase_30d/`
(Contains `evaluation_report.json`, `model_audit_report.json`, `predictions.parquet`, `feature_importance.parquet`, and the frozen model artifact).

---

### 23. Behavioral Segmentation Discovery (Phase 2)

**STATUS:** FROZEN (Phase 2 Complete)

**Objective:** Discover stable, operationally useful customer behavioral segments from the Customer 360 temporal features.

**Algorithm:** K-Means, K=4 (Final Business Selection)

> K=4 is selected on **BUSINESS INTERPRETABILITY and OPERATIONAL USEFULNESS**, not because it is the silhouette-score optimum. K=2 collapses useful behavioral distinctions; K=3 merges meaningful populations; K=5/6 produce pathological micro-clusters with no distinct operational cohort.

**Canonical Segment Labels:**

| Cluster | Segment Name | Size |
|---|---|---|
| 0 | Dormant Multi-Buyers | 1,727 (32.9%) |
| 1 | Active High-Value | 572 (10.9%) |
| 2 | Recent Repeat Buyers | 1,263 (24.1%) |
| 3 | One-Time Dormant | 1,685 (32.1%) |

**Frequency Stabilization:**
- Canonical `FEATURE_purchase_frequency` divides orders by `customer_lifetime_days`, producing pathological values for customers with very short lifetimes.
- A segmentation-specific feature `SEG_purchase_frequency_stable` was created using `purchase_order_count / max(lifetime_days, 90) * 30`, stabilizing new-customer frequency.
- This feature is used only for segmentation; canonical Customer 360 features remain untouched.

**Stability Validation (Authoritative):**
- **ARI (stable vs unstable frequency):** 0.5882
- **Pathological cluster size (unstable representation):** 62 customers
- These are the single authoritative values. Earlier documentation referencing ARI ≈ 0.4771 or 17-customer micro-cluster referred to a prior iteration of the analysis and is superseded.

**Experiment Output Location:**
`backend/training/experiments/segmentation/`
(Contains `segmentation_model.pkl`, `segmentation_validation_report.json`, `cluster_profiles.csv`, `cluster_labels.json`, `segment_propensity_preview.csv`.)

---

### 24. Segment × Propensity Combination (Phase 3)

**STATUS:** FROZEN (Phase 3 Complete)

**Objective:** Combine the frozen Phase 2 behavioral segmentation with the frozen Phase 1 30-day propensity scores to create a unified customer intelligence table.

**As-of-Date Invariant:**
- Both segment and propensity refer to the same customer state as of `2011-08-31`.
- Zero tolerance: no date mismatches, no missing segments, no missing propensity scores.

**Customers:** 5,247

**Propensity Distribution:**

| Band | Threshold | Count | % |
|---|---|---|---|
| 1_LOW | < 0.16 | 3,272 | 62.4% |
| 2_MODERATE | 0.16 – < 0.27 | 960 | 18.3% |
| 3_HIGH | 0.27 – < 0.40 | 511 | 9.7% |
| 4_VERY_HIGH | ≥ 0.40 | 504 | 9.6% |

**Segment × Propensity Matrix (Row-Normalised %):**

| Segment | LOW | MODERATE | HIGH | VERY_HIGH |
|---|---|---|---|---|
| Active High-Value | 0.9% | 3.7% | 18.5% | **76.9%** |
| Recent Repeat Buyers | 20.8% | **49.1%** | 25.0% | 5.1% |
| Dormant Multi-Buyers | **76.5%** | 18.4% | 5.2% | 0.0% |
| One-Time Dormant | **99.9%** | 0.1% | 0.0% | 0.0% |

> **Note:** Cells with very small counts (e.g., One-Time Dormant + MODERATE = 2 customers) must not be over-interpreted. They are preserved for completeness.

**Validation Results:** All 6 checks passed (5,247 customers, 1 unique date, 0 missing segments, 0 missing propensity, 0 date mismatches, 0 duplicates).

**Experiment Output Location:**
`backend/training/experiments/intelligence/`
(Contains `06_segment_propensity_matrix.ipynb`, `combined_intelligence.csv`, `segment_propensity_matrix.json`.)

---

### 25. Phase 4: Why + What Next + Confidence + Evidence

**STATUS:** COMPLETE

**Objective:** Transform the Phase 3 customer state (Segment + Propensity Score + Propensity Band) into a deterministic, auditable customer intelligence object containing WHY, WHAT NEXT, CONFIDENCE, and EVIDENCE.

**Architecture:**

```
Customer 360 Features
         ↓
Behavioral Segmentation (frozen Phase 2)
         ↓
30-day Propensity Score (frozen Phase 1)
         ↓
Segment × Propensity (Phase 3)
         ↓
Behavioral Signal Engine (customer-vs-self baselines)
         ↓
Why Engine (deterministic, traceable explanations)
         ↓
Action Policy (JSON-configured, priority-ordered rules)
         ↓
Confidence + Evidence Assembly
         ↓
Customer Intelligence Object (JSON-serializable)
```

**No LLMs are used at any point.** All recommendations, explanations, and evidence are deterministic and traceable to actual numerical conditions.

---

#### 25.1 Behavioral Signals

All signals compare current customer state to that customer's own historical behavior (not global population averages), using only features available at `as_of_date`. Future targets are strictly excluded.

| Signal | Definition | Threshold | Evidence Format |
|---|---|---|---|
| `recency_elevated` | `recency_days / (lifetime_days / max(orders, 1))` ≥ 2.0 | 2.0× normal interval | `recency_ratio: float` |
| `spend_declining` | `net_spend_90d / ((total_net_spend / max(lifetime_days,90)) × 90)` ≤ 0.70 | < 70% of historical 90-day baseline | `spend_ratio: float` |
| `frequency_declining` | `orders_90d / ((total_orders / max(lifetime_days,90)) × 90)` ≤ 0.50 | < 50% of historical 90-day cadence | `freq_ratio: float` |
| `return_risk` | `FEATURE_return_rate` > 0.15 AND `return_line_count` > 0 | > 15% return rate | `return_rate: float` |

**Leakage Safeguards:**
- `recency_elevated` requires minimum 30 days history AND ≥ 2 orders.
- `spend_declining` requires minimum 90 days history AND positive total spend.
- `frequency_declining` requires minimum 90 days history AND ≥ 3 orders.
- `return_risk` requires at least one confirmed return line. Customers in Online Retail II with zero returns (identified customers, where refunds are coded as cancellations) will never trigger this signal, which is semantically correct.

---

#### 25.2 Action Policy

**Configuration:** `backend/config/intelligence_action_policy.json`

Policy rules are evaluated in descending priority order. Exactly one primary recommendation is emitted per customer.

| Rule ID | Priority | Conditions | Recommendation |
|---|---|---|---|
| `RETURN_RISK_01` | 100 | `return_risk = true` | Margin-aware retention review |
| `WINBACK_01` | 90 | Dormant Multi-Buyers + LOW/MODERATE + `recency_elevated = true` | High-value reactivation / win-back |
| `RETENTION_01` | 80 | Active High-Value + HIGH/VERY_HIGH + `spend_declining = true` | Proactive retention offer |
| `CROSS_SELL_01` | 70 | Active High-Value + HIGH/VERY_HIGH | Light-touch cross-sell |
| `NURTURE_01` | 60 | Recent Repeat Buyers + MODERATE/HIGH | Targeted Nurture |
| `NO_ACTION_01` | 50 | One-Time Dormant + LOW | No Action / Minimum Target |
| `DEFAULT_01` | 0 | *(any)* | Standard engagement |

**Conflict Resolution:** Higher priority rules are evaluated first. The first matching rule wins unconditionally.

---

#### 25.3 Confidence Methodology

Confidence represents how strongly the evidence supports the given recommendation — it is NOT the propensity score.

| Confidence | Condition |
|---|---|
| High | `customer_lifetime_days` ≥ 90 AND matched a specific non-fallback rule |
| Medium | `customer_lifetime_days` ≥ 30 AND matched a specific non-fallback rule |
| Low | `customer_lifetime_days` < 30 OR matched fallback (`DEFAULT_01` / `FALLBACK_00`) |

---

#### 25.4 Intelligence Object Schema

```json
{
  "customer_id": "string",
  "as_of_date": "YYYY-MM-DD",
  "segment": "string",
  "purchase_probability_30d": 0.0,
  "propensity_band": "string",
  "recommendation": "string",
  "recommendation_confidence": "High|Medium|Low",
  "policy_rule_id": "string",
  "why": ["string", ...],
  "evidence": [
    {
      "signal": "string",
      "value": 0.0,
      "threshold": 0.0,
      "message": "string"
    }
  ],
  "behavioral_signals": {
    "recency_elevated": true,
    "spend_declining": false,
    "frequency_declining": false,
    "return_risk": false
  }
}
```

---

#### 25.5 Phase 4 Modules

**`backend/ml/intelligence_engine.py`**
- Accepts a merged customer row (Phase 3 state + temporal features)
- Computes all behavioral signals using customer-vs-self baselines
- Calls `ActionPolicy.evaluate()` for recommendation
- Calls `ActionPolicy.get_confidence()` for confidence
- Returns a fully populated canonical intelligence object
- `process_batch()` handles the full 5,247-customer dataset

**`backend/rules/action_policy.py`**
- Loads and validates `intelligence_action_policy.json`
- Sorts rules by priority on load
- `evaluate()` evaluates all conditions deterministically; returns first match
- `get_confidence()` derives confidence from history depth and rule type

**`backend/config/intelligence_action_policy.json`**
- Single canonical policy configuration
- Contains: `signals` (thresholds), `rules` (conditions + priority + recommendation), `confidence_rules`

---

#### 25.6 Batch Results (Phase 4)

**Customers processed:** 5,247  
**Duplicate customer IDs:** 0  
**As-of-date consistent:** Yes (2011-08-31)  
**Leakage check passed:** Yes  
**Fallback recommendations:** 0  

**Recommendation Distribution:**

| Recommendation | Count |
|---|---|
| No Action / Minimum Target | 1,683 |
| High-value reactivation / win-back | 1,117 |
| Standard engagement | 965 |
| Targeted Nurture | 936 |
| Light-touch cross-sell | 345 |
| Proactive retention offer | 201 |

**Confidence Distribution:**

| Confidence | Count |
|---|---|
| Low | 2,638 |
| High | 2,300 |
| Medium | 309 |

**Signal Prevalence:**

| Signal | Customers Triggered |
|---|---|
| spend_declining | 2,103 |
| recency_elevated | 1,450 |
| frequency_declining | 1,335 |
| return_risk | 0 |

**Experiment Output Location:**
`backend/training/experiments/intelligence/`
(Contains `customer_intelligence.parquet`, `phase4_validation_report.json` in addition to Phase 3 artifacts.)

---

#### 25.7 Phase 4.1: Quality Freeze Audit

A rigorous quality freeze audit was conducted on Phase 4 outputs before locking the phase.

**1. Missing Evidence Semantics:**
- **Finding:** 2,850 customers lacked active `why` / `evidence` fields.
- **Resolution:** This is mathematically correct. If a customer is One-Time Dormant, they cannot have a declining frequency relative to their own non-existent baseline. We introduced an explicit `evidence_status` field.
- **Evidence Status Distribution:**
  - `EVIDENCE_PRESENT`: 2,397
  - `NO_ACTIVE_SIGNALS`: 2,238 (History exists, but no deviation from baseline triggered)
  - `INSUFFICIENT_HISTORY`: 612 (Customer history < 30 days, cannot compute baseline)

**2. Return Risk:**
- **Finding:** `return_risk` triggered 0 times.
- **Resolution:** Verified as a structural reality of the Online Retail II dataset, not a code bug. Identified customers in this dataset have refunds coded exclusively as cancellations (Invoice prefix 'C'). Returns without the 'C' prefix are assigned to guests. The code correctly handles this semantic reality.

**3. Confidence Semantics:**
- **Finding:** 2,638 customers received `Low` confidence.
- **Resolution:** Verified that confidence explicitly measures **confidence in the behavioral evidence**, NOT the likelihood of purchase (propensity). A customer can have a High propensity to buy but Low confidence in the specific behavioral recommendation if they have insufficient history or fall into the fallback `DEFAULT_01` bucket.

---

#### 25.8 Testing

**Phase 4 Test File:** `backend/tests/test_intelligence_engine.py`

Tests cover:
- Determinism (same input → identical output, two runs)
- Rule precedence (higher-priority rule wins over lower-priority)
- Fallback handling (unknown segment → DEFAULT_01 → Low confidence)
- JSON serialization (no NumPy/datetime serialization failures)
- As-of-date leakage protection (TARGET column excluded from output)

**Test Results (full suite):**
- Existing tests: 30 passed
- Phase 4 tests: 5 passed
- **Total: 35 passed, 0 failed**
- **Batch Determinism:** 100% match on double-execution.

---

#### 25.9 Production Code Status

| File | Status |
|---|---|
| `backend/api/main.py` | NOT MODIFIED |
| `backend/api/gateway.py` | NOT MODIFIED |
| `frontend/app.py` | NOT MODIFIED |
| `backend/ml/model_server.py` | NOT MODIFIED |
| `backend/rules/rules_engine.py` | NOT MODIFIED |
| `backend/rules/campaign_generator.py` | NOT MODIFIED |
| `backend/rules/campaign_orchestrator.py` | NOT MODIFIED |

**Phase 4 is an independent analytical intelligence layer. No API or dashboard integration has been performed. Production API/dashboard integration is Phase 5 (NOT STARTED).**

---

#### 25.10 Phase Boundary

| Phase | Status |
|---|---|
| Phase 1 — 30d Next-Purchase Propensity | FROZEN |
| Phase 2 — Behavioral Segmentation | FROZEN |
| Phase 3 — Segment × Propensity Combination | FROZEN |
| Phase 4 — Why + What Next + Confidence + Evidence | FROZEN |
| Phase 4.1 — Quality Freeze | FROZEN |
| Phase 5 — Production API Integration | NOT STARTED |
| Phase 6 — Dashboard Integration | NOT STARTED |
