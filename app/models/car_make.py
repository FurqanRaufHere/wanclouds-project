from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session, relationship

from app.db.base import Base


class CarMake(Base):
    __tablename__ = "car_makes"

    # Field key constants
    ID_KEY = "id"
    NAME_KEY = "name"

    # Column length constants
    NAME_MAX_LEN = 100

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(NAME_MAX_LEN), unique=True, nullable=False)

    # A make has many models; deleting a make cascades to its models (and their years).
    models = relationship(
        "CarModel",
        back_populates="make",
        cascade="all, delete-orphan",
    )

    def to_json(self) -> dict:
        return {self.ID_KEY: self.id, self.NAME_KEY: self.name}


def get_or_create_make(db: Session, name: str) -> "CarMake":
    """Return the CarMake with this name, creating it if needed."""
    make = db.query(CarMake).filter(CarMake.name == name).first()
    if make is None:
        make = CarMake(name=name)
        db.add(make)
        db.flush()
    return make
