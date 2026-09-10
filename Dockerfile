# Customer Intelligence & Campaign Orchestration Platform (CICOP)
# Multi-stage Docker build for production deployment

# Stage 1: Base Python environment
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    gcc \
    g++ \
    make \
    libssl-dev \
    libffi-dev \
    pkg-config \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend and frontend
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY README.md TECHNICAL.md .env.example ./

# Create necessary directories
RUN mkdir -p backend/data backend/logs backend/models backend/config

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Generate sample data if not exists
RUN python -c "import os, runpy; \
    os.makedirs('backend/data', exist_ok=True); \
    0 if os.path.exists('backend/data/customer_insights.db') else runpy.run_path('backend/scripts/generate_standalone_data.py')"

EXPOSE 8000 8001 8002 8501

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Stage 2: ML Model Serving
FROM base as ml-serving
EXPOSE 8001
CMD ["uvicorn", "backend.ml.model_server:app", "--host", "0.0.0.0", "--port", "8001"]

# Stage 3: API Gateway
FROM base as api-gateway
EXPOSE 8002
CMD ["uvicorn", "backend.api.gateway:app", "--host", "0.0.0.0", "--port", "8002"]

# Stage 4: Worker Processes
FROM base as worker
CMD ["celery", "-A", "backend.workers.celery_app", "worker", "--loglevel=info"]

# Stage 5: Streamlit Frontend
FROM base as frontend
EXPOSE 8501
CMD ["streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
