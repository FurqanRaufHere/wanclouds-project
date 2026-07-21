from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Session, relationship

from app.db.base import Base


class CarModel(Base):
    __tablename__ = "car_models"

    # A model name is unique within a make, not globally
    # (e.g. two makes could each have a "3").
    __table_args__ = (
        UniqueConstraint("make_id", "name", name="uq_model_make_name"),
    )

    # Field key constants
    ID_KEY = "id"
    NAME_KEY = "name"
    MAKE_ID_KEY = "make_id"

    # Column length constants
    NAME_MAX_LEN = 100

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(NAME_MAX_LEN), nullable=False)
    make_id = Column(Integer, ForeignKey("car_makes.id"), nullable=False)

    # Many models belong to one make.
    make = relationship("CarMake", back_populates="models")
    # A model has many years; deleting a model cascades to its years.
    years = relationship(
        "CarYear",
        back_populates="model",
        cascade="all, delete-orphan",
    )


def get_or_create_model(db: Session, make_id: int, name: str) -> "CarModel":
    """Return the CarModel with this name under the given make, creating it if needed."""
    model = (
        db.query(CarModel)
        .filter(CarModel.make_id == make_id, CarModel.name == name)
        .first()
    )
    if model is None:
        model = CarModel(make_id=make_id, name=name)
        db.add(model)
        db.flush()
    return model
