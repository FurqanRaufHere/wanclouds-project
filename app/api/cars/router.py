from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.cars.schemas import CarResponse, CarsListResponse, CarUpdateRequest
from app.api.cars.utils import (
    delete_car,
    get_car_or_404,
    get_cars_paginated,
    update_car,
)
from app.common.schemas import PaginationQuerySchema
from app.core.dependencies import authenticate
from app.db.database import DbSession

router = APIRouter(prefix="/cars", tags=["Cars"])


# Routes
@router.get("/", response_model=CarsListResponse)
@authenticate
def list_cars(db: DbSession, pagination: Annotated[PaginationQuerySchema, Query()]):
    items, total = get_cars_paginated(db, pagination.offset, pagination.limit)
    return CarsListResponse.create(items, total, pagination)


@router.get("/{car_id}", response_model=CarResponse)
@authenticate
def get_car(car_id: str, db: DbSession):
    return get_car_or_404(db, car_id)


@router.put("/{car_id}", response_model=CarResponse)
@authenticate
def edit_car(car_id: str, payload: CarUpdateRequest, db: DbSession):
    car = get_car_or_404(db, car_id)
    return update_car(db, car, payload.model_dump(exclude_unset=True))


@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
@authenticate
def remove_car(car_id: str, db: DbSession):
    car = get_car_or_404(db, car_id)
    delete_car(db, car)
