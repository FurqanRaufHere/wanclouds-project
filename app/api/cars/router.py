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
from app.db.database import get_db

router = APIRouter(prefix="/cars", tags=["Cars"])


# Routes
@router.get("/", response_model=CarsListResponse)
@authenticate
def list_cars(pagination: Annotated[PaginationQuerySchema, Query()]):
    with get_db() as db:
        items, total = get_cars_paginated(db, pagination.skip, pagination.limit)
        return CarsListResponse(total=total, skip=pagination.skip, limit=pagination.limit, items=items)


@router.put("/{car_id}", response_model=CarResponse)
@authenticate
def edit_car(car_id: str, payload: CarUpdateRequest):
    with get_db() as db:
        car = get_car_or_404(db, car_id)
        car = update_car(db, car, payload.model_dump(exclude_unset=True))
        # Build the response while the session is still open: make/model/year
        # are lazy-loaded relationships, and get_db() closes the session on exit.
        return CarResponse.model_validate(car)


@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
@authenticate
def remove_car(car_id: str):
    with get_db() as db:
        car = get_car_or_404(db, car_id)
        delete_car(db, car)
