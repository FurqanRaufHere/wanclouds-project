from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.cars.schemas import CarResponse, CarsListResponse, CarUpdateRequest
from app.api.cars.utils import get_car_or_404
from app.common.schemas import PaginationQuerySchema
from app.core.dependencies import authenticate
from app.db.database import get_db
from app.models.car_make import get_or_create_makes
from app.models.car_model import get_or_create_models
from app.models.car_year import get_or_create_years
from app.models.cars import Car

router = APIRouter(prefix="/cars", tags=["Cars"])


# Routes
@router.get("/", response_model=CarsListResponse)
@authenticate
def get_cars(pagination: Annotated[PaginationQuerySchema, Query()]):
    with get_db() as db:
        cars = db.query(Car).offset(pagination.skip).limit(pagination.limit).all()
        total = db.query(Car).count()
        return CarsListResponse(total=total, skip=pagination.skip, limit=pagination.limit, items=cars)


@router.put("/{car_id}", response_model=CarResponse)
@authenticate
def update_car(car_id: str, payload: CarUpdateRequest):
    with get_db() as db:
        car = get_car_or_404(car_id, db)
        update_data = payload.model_dump(exclude_unset=True)

        if "make" in update_data:
            name = update_data.pop("make")
            car.make_id = get_or_create_makes(db, [name])[name]
        if "model" in update_data:
            name = update_data.pop("model")
            car.model_id = get_or_create_models(db, [name])[name]
        if "year" in update_data:
            year = update_data.pop("year")
            car.year_id = get_or_create_years(db, [year])[year] if year is not None else None

        for field, value in update_data.items():
            setattr(car, field, value)
        db.commit()
        db.refresh(car)
        return car


@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
@authenticate
def delete_car(car_id: str):
    with get_db() as db:
        car = get_car_or_404(car_id, db)
        db.delete(car)
        db.commit()
