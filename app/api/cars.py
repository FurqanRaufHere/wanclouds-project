from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.core.dependencies import get_current_user
from app.db.database import get_db_session
from app.models.cars import Car
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/cars",
    tags=["Cars"],
    dependencies=[Depends(get_current_user)]  # protects ALL routes automatically
)


# Schemas
class CarResponse(BaseModel):
    id: int
    make: str
    model: str
    category: str | None
    year: int | None

    model_config = {"from_attributes": True}


class CarsListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    cars: list[CarResponse]


class CarUpdateRequest(BaseModel):
    make: str | None = None
    model: str | None = None
    category: str | None = None
    year: int | None = None


def get_car_or_404(car_id: int, db: Session) -> Car:
    car = db.query(Car).filter(Car.id == car_id).first()
    if car is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Car with id {car_id} not found"
        )
    return car


# Common pagination dependency
def pagination(skip: int = 0, limit: int = 20):
    return {"skip": skip, "limit": limit}


# Routes
@router.get("/", response_model=CarsListResponse)
def get_cars(
    db: Session = Depends(get_db_session),
    pages: dict = Depends(pagination)
):
    skip = pages["skip"]
    limit = pages["limit"]
    cars = db.query(Car).offset(skip).limit(limit).all()
    total = db.query(Car).count()
    return CarsListResponse(total=total, skip=skip, limit=limit, cars=cars)


@router.put("/{car_id}", response_model=CarResponse)
def update_car(
    car_id: int,
    payload: CarUpdateRequest,
    db: Session = Depends(get_db_session)
):
    car = get_car_or_404(car_id, db)
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(car, field, value)
    db.commit()
    db.refresh(car)
    return car


@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_car(
    car_id: int,
    db: Session = Depends(get_db_session)
):
    car = get_car_or_404(car_id, db)
    db.delete(car)
    db.commit()
