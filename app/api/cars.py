from fastapi import APIRouter, Depends
from app.tasks.fetch_cars import fetch_cars_task
from app.core.dependencies import get_current_user
from app.models.user import User
from app.db.database import SessionLocal
from app.models.cars import Car

router = APIRouter(prefix="/cars", tags=["Cars"])


@router.post("/fetch")
def trigger_fetch(current_user: User = Depends(get_current_user)):
    task = fetch_cars_task.delay()
    return {
        "message": "Car fetch task started in background",
        "task_id": task.id,
        "status": "queued"
    }


@router.get("/status/{task_id}")
def get_task_status(task_id: str, current_user: User = Depends(get_current_user)):
    from app.celery_app import celery_app
    task = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.ready() else None
    }


@router.get("/")
def get_cars(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    db = SessionLocal()
    try:
        cars = db.query(Car).offset(skip).limit(limit).all()
        total = db.query(Car).count()
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "cars": [
                {
                    "id": car.id,
                    "make": car.make,
                    "model": car.model,
                    "category": car.category,
                    "year": car.year
                }
                for car in cars
            ]
        }
    finally:
        db.close()
