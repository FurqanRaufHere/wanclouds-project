from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.cars.schemas import CarResponse, CarsListResponse, CarUpdateRequest
from app.common.schemas import PaginationQuerySchema
from app.core.dependencies import authenticate
from app.db.database import get_db
from app.models.cars import Car

router = APIRouter(prefix="/cars", tags=["Cars"])


# Routes
@router.get("/", response_model=CarsListResponse)
@authenticate
def get_cars(pagination: Annotated[PaginationQuerySchema, Query()]):
    with get_db() as db:
        items, total = Car.get_paginated(db, pagination.skip, pagination.limit)
        return CarsListResponse(total=total, skip=pagination.skip, limit=pagination.limit, items=items)


@router.put("/{car_id}", response_model=CarResponse)
@authenticate
def update_car(car_id: str, payload: CarUpdateRequest):
    with get_db() as db:
        car = Car.get_or_404(db, car_id)
        return car.apply_update(db, payload.model_dump(exclude_unset=True))


@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
@authenticate
def delete_car(car_id: str):
    with get_db() as db:
        car = Car.get_or_404(db, car_id)
        car.delete(db)
