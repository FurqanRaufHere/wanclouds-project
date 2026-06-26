from typing import Iterable

from sqlalchemy import Column, Integer
from sqlalchemy.orm import Session

from app.db.base import Base


class CarYear(Base):
    __tablename__ = "car_years"

    # Field key constants
    ID_KEY = "id"
    YEAR_KEY = "year"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, unique=True, nullable=False)

    def to_json(self) -> dict:
        return {self.ID_KEY: self.id, self.YEAR_KEY: self.year}


def get_or_create_years(db: Session, years: Iterable[int]) -> dict[int, int]:
    years = {year for year in years if year is not None}
    if not years:
        return {}

    existing = db.query(CarYear).filter(CarYear.year.in_(years)).all()
    year_to_id = {row.year: row.id for row in existing}

    missing = years - year_to_id.keys()
    if missing:
        new_rows = [CarYear(year=year) for year in missing]
        db.add_all(new_rows)
        db.flush()
        year_to_id.update({row.year: row.id for row in new_rows})

    return year_to_id
