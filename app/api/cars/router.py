from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.api.cars.schemas import CarResponse, CarsListResponse, CarUpdateRequest
from app.common.schemas import PaginationQuerySchema
from app.core.dependencies import authenticate
from app.db.database import get_db_session
from app.models.car_make import get_or_create_make
from app.models.car_model import get_or_create_model
from app.models.car_year import get_or_create_year
from app.models.cars import Car

router = APIRouter(prefix="/cars", tags=["Cars"])


@router.get("/", response_model=CarsListResponse)
@authenticate
def list_cars(
    pagination: Annotated[PaginationQuerySchema, Query()],
    db: Session = Depends(get_db_session),
):
    items = (
        db.query(Car)
        # make/model/year live in their own tables; join them up front so
        # serializing a page is one query instead of three per car.
        .options(
            joinedload(Car.make_rel),
            joinedload(Car.model_rel),
            joinedload(Car.year_rel),
        )
        # Order explicitly: without it MySQL may return rows in a different
        # order per query, so pages could repeat or skip cars.
        .order_by(Car.id)
        .offset(pagination.skip)
        .limit(pagination.limit)
        .all()
    )
    total = db.query(Car).count()
    return CarsListResponse(
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
        items=items,
    )


@router.put("/{car_id}", response_model=CarResponse)
@authenticate
def edit_car(
    car_id: str,
    payload: CarUpdateRequest,
    db: Session = Depends(get_db_session),
):
    car = get_car_or_404(db, car_id)

    fields = payload.model_dump(exclude_unset=True)
    if any(key in fields for key in (Car.MAKE_KEY, Car.MODEL_KEY, Car.YEAR_KEY)):
        # Pops make/model/year off `fields` and sets the FK columns instead,
        # so the loop below only sees the car's own columns.
        apply_make_model_year(db, car, fields)

    for field, value in fields.items():
        setattr(car, field, value)

    db.commit()
    db.refresh(car)
    return car


@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
@authenticate
def remove_car(car_id: str, db: Session = Depends(get_db_session)):
    car = get_car_or_404(db, car_id)
    db.delete(car)
    db.commit()


def get_car_or_404(db: Session, car_id: str) -> Car:
    car = db.query(Car).filter(Car.id == car_id).first()
    if car is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Car with id {car_id} not found",
        )
    return car


def apply_make_model_year(db: Session, car: Car, fields: dict) -> None:
    """Resolve the make -> model -> year hierarchy onto the car's FK columns.

    A model is scoped to its make and a year to its model, so the three have to
    be resolved together, top down. Any part the payload doesn't change falls
    back to the car's current value.
    """
    # `or car.<field>` rather than a pop() default: the key is present but None
    # when the client explicitly sends null, and make/model are NOT NULL.
    make_name = fields.pop(Car.MAKE_KEY, None) or car.make
    model_name = fields.pop(Car.MODEL_KEY, None) or car.model
    year_value = fields.pop(Car.YEAR_KEY, car.year)

    make = get_or_create_make(db, make_name)
    model = get_or_create_model(db, make.id, model_name)

    car.make_id = make.id
    car.model_id = model.id
    car.year_id = (
        get_or_create_year(db, model.id, year_value).id
        if year_value is not None
        else None
    )
