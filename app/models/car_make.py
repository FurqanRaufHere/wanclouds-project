from typing import Iterable

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session

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

    def to_json(self) -> dict:
        return {self.ID_KEY: self.id, self.NAME_KEY: self.name}


def get_or_create_makes(db: Session, names: Iterable[str]) -> dict[str, int]:
    names = {name for name in names if name is not None}
    if not names:
        return {}

    existing = db.query(CarMake).filter(CarMake.name.in_(names)).all()
    name_to_id = {row.name: row.id for row in existing}

    missing = names - name_to_id.keys()
    if missing:
        new_rows = [CarMake(name=name) for name in missing]
        db.add_all(new_rows)
        db.flush()
        name_to_id.update({row.name: row.id for row in new_rows})

    return name_to_id
