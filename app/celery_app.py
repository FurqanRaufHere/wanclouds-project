from celery import Celery
from app.core.config import REDIS_URL

# Create Celery instance
# broker = where tasks are sent (Redis)
# backend = where results are stored (also Redis)
celery_app = Celery(
    "worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks.fetch_cars"]
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)
