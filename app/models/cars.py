import uuid

from fastapi import HTTPException, status
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Session, relationship

from app.db.base import Base
from app.models.car_make import CarMake, get_or_create_make
from app.models.car_model import CarModel, get_or_create_model
from app.models.car_year import CarYear, get_or_create_year


class Car(Base):
    __tablename__ = "cars"

    # Field key constants
    ID_KEY = "id"
    MAKE_KEY = "make"
    MODEL_KEY = "model"
    CATEGORY_KEY = "category"
    YEAR_KEY = "year"
    OBJECT_ID_KEY = "object_id"

    # Column length constants
    ID_LEN = 32
    CATEGORY_MAX_LEN = 100
    OBJECT_ID_MAX_LEN = 100

    id = Column(String(ID_LEN), primary_key=True, default=lambda: uuid.uuid4().hex, index=True)
    make_id = Column(Integer, ForeignKey("car_makes.id"), nullable=False)
    model_id = Column(Integer, ForeignKey("car_models.id"), nullable=False)
    category = Column(String(CATEGORY_MAX_LEN), nullable=True)
    year_id = Column(Integer, ForeignKey("car_years.id"), nullable=True)
    object_id = Column(String(OBJECT_ID_MAX_LEN), unique=True, nullable=False)

    make_rel = relationship(CarMake)
    model_rel = relationship(CarModel)
    year_rel = relationship(CarYear)

    def __init__(
        self,
        make_id: int,
        model_id: int,
        object_id: str,
        category: str | None = None,
        year_id: int | None = None,
        id: str | None = None,
    ):
        self.id = id or uuid.uuid4().hex
        self.make_id = make_id
        self.model_id = model_id
        self.category = category
        self.year_id = year_id
        self.object_id = object_id

    @property
    def make(self) -> str | None:
        return self.make_rel.name if self.make_rel else None

    @property
    def model(self) -> str | None:
        return self.model_rel.name if self.model_rel else None

    @property
    def year(self) -> int | None:
        return self.year_rel.year if self.year_rel else None

    def to_json(self) -> dict:
        return {
            self.ID_KEY: self.id,
            self.MAKE_KEY: self.make,
            self.MODEL_KEY: self.model,
            self.CATEGORY_KEY: self.category,
            self.YEAR_KEY: self.year,
            self.OBJECT_ID_KEY: self.object_id,
        }

    # Data-access / business logic lives on the model so routers stay thin.
    @classmethod
    def get_paginated(cls, db: Session, skip: int, limit: int) -> tuple[list["Car"], int]:
        items = db.query(cls).offset(skip).limit(limit).all()
        total = db.query(cls).count()
        return items, total

    @classmethod
    def get_or_404(cls, db: Session, car_id: str) -> "Car":
        car = db.query(cls).filter(cls.id == car_id).first()
        if car is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Car with id {car_id} not found",
            )
        return car

    def apply_update(self, db: Session, data: dict) -> "Car":
        # make/model/year form a hierarchy, so resolve them together: a model is
        # scoped to its make, and a year to its model. Fall back to this car's
        # current values for any part of the hierarchy the payload doesn't change.
        if any(key in data for key in (self.MAKE_KEY, self.MODEL_KEY, self.YEAR_KEY)):
            make_name = data.pop(self.MAKE_KEY, self.make)
            model_name = data.pop(self.MODEL_KEY, self.model)
            year_value = data.pop(self.YEAR_KEY, self.year)

            make = get_or_create_make(db, make_name)
            model = get_or_create_model(db, make.id, model_name)
            self.make_id = make.id
            self.model_id = model.id
            self.year_id = (
                get_or_create_year(db, model.id, year_value).id
                if year_value is not None
                else None
            )

        for field, value in data.items():
            setattr(self, field, value)
        db.commit()
        db.refresh(self)
        return self

    def delete(self, db: Session) -> None:
        db.delete(self)
        db.commit()
