from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.cars import Car


def get_car_or_404(car_id: str, db: Session) -> Car:
    car = db.query(Car).filter(Car.id == car_id).first()
    if car is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Car with id {car_id} not found"
        )
    return car
