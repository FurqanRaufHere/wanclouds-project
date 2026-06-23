from celery import Celery
from app.core.config import REDIS_URL

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
    beat_schedule={
        "fetch-cars-every-24-hours": {
            "task": "fetch_cars",
            "schedule": 86400.0,  # 86400 seconds = 24 hours
        },
    }
)
