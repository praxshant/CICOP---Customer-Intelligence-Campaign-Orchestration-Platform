# src/workers/celery_app.py
import os
from celery import Celery
from celery.schedules import crontab
import httpx
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("CELERY_BROKER_URL", os.getenv("REDIS_URL", "redis://localhost:6379/0"))
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)
ML_SERVING_URL = os.getenv("ML_SERVING_URL", "http://cicop-ml-serving:8001")

celery_app = Celery(
    "cicop",
    broker=REDIS_URL,
    backend=RESULT_BACKEND,
)

@celery_app.task
def sample_task(x: int, y: int) -> int:
    return x + y

@celery_app.task
def healthcheck() -> str:
    return "ok"

# Legacy retraining tasks have been deprecated and removed.
celery_app.conf.beat_schedule = {}
