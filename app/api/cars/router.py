from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.cars import utils
from app.api.cars.schemas import CarResponse, CarsListResponse, CarUpdateRequest
from app.common.schemas import PaginationQuerySchema
from app.core.dependencies import authenticate
from app.db.database import get_db

router = APIRouter(prefix="/cars", tags=["Cars"])


# Routes
@router.get("/", response_model=CarsListResponse)
@authenticate
def get_cars(pagination: Annotated[PaginationQuerySchema, Query()]):
    with get_db() as db:
        items, total = utils.get_cars_paginated(db, pagination.skip, pagination.limit)
        return CarsListResponse(total=total, skip=pagination.skip, limit=pagination.limit, items=items)


@router.put("/{car_id}", response_model=CarResponse)
@authenticate
def update_car(car_id: str, payload: CarUpdateRequest):
    with get_db() as db:
        car = utils.get_car_or_404(db, car_id)
        return utils.update_car(db, car, payload.model_dump(exclude_unset=True))


@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
@authenticate
def delete_car(car_id: str):
    with get_db() as db:
        car = utils.get_car_or_404(db, car_id)
        utils.delete_car(db, car)
