import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "monitor_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["tasks"]
)
