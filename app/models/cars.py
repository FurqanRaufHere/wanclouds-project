import uuid

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.car_make import CarMake
from app.models.car_model import CarModel
from app.models.car_year import CarYear


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
