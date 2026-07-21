from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.car_make import get_or_create_make
from app.models.car_model import get_or_create_model
from app.models.car_year import get_or_create_year
from app.models.cars import Car


def get_cars_paginated(db: Session, skip: int, limit: int) -> tuple[list[Car], int]:
    items = db.query(Car).offset(skip).limit(limit).all()
    total = db.query(Car).count()
    return items, total


def get_car_or_404(db: Session, car_id: str) -> Car:
    car = db.query(Car).filter(Car.id == car_id).first()
    if car is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Car with id {car_id} not found",
        )
    return car


def update_car(db: Session, car: Car, data: dict) -> Car:
    # make/model/year form a hierarchy, so resolve them together: a model is
    # scoped to its make, and a year to its model. Fall back to this car's
    # current values for any part of the hierarchy the payload doesn't change.
    if any(key in data for key in (Car.MAKE_KEY, Car.MODEL_KEY, Car.YEAR_KEY)):
        make_name = data.pop(Car.MAKE_KEY, car.make)
        model_name = data.pop(Car.MODEL_KEY, car.model)
        year_value = data.pop(Car.YEAR_KEY, car.year)

        make = get_or_create_make(db, make_name)
        model = get_or_create_model(db, make.id, model_name)
        car.make_id = make.id
        car.model_id = model.id
        car.year_id = (
            get_or_create_year(db, model.id, year_value).id
            if year_value is not None
            else None
        )

    for field, value in data.items():
        setattr(car, field, value)
    db.commit()
    db.refresh(car)
    return car


def delete_car(db: Session, car: Car) -> None:
    # A car only *references* make/model/year (many-to-one); it is the child
    # side of those FKs and nothing references a car in turn. So deleting a car
    # is a single DELETE on the cars row: it is never blocked by a relationship,
    # and it never cascades into the shared make/model/year lookup rows.
    db.delete(car)
    db.commit()
