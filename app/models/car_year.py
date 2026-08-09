from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Session, relationship

from app.db.base import Base


class CarYear(Base):
    __tablename__ = "car_years"

    # A year is unique within a model, not globally
    # (thousands of models share the year 2020).
    __table_args__ = (
        UniqueConstraint("model_id", "year", name="uq_year_model_year"),
    )

    # Field key constants
    ID_KEY = "id"
    YEAR_KEY = "year"
    MODEL_ID_KEY = "model_id"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)
    model_id = Column(Integer, ForeignKey("car_models.id"), nullable=False)

    # Many years belong to one model.
    model = relationship("CarModel", back_populates="years")


def get_or_create_year(db: Session, model_id: int, year: int) -> "CarYear":
    """Return the CarYear for this year under the given model, creating it if needed."""
    row = (
        db.query(CarYear)
        .filter(CarYear.model_id == model_id, CarYear.year == year)
        .first()
    )
    if row is None:
        row = CarYear(model_id=model_id, year=year)
        db.add(row)
        db.flush()
    return row
