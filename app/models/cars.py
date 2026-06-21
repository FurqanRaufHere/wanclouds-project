from sqlalchemy import Column, Integer, String
from app.db.base import Base


class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    make = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    category = Column(String(100), nullable=True)
    year = Column(Integer, nullable=True)
    object_id = Column(String(100), unique=True, nullable=False)
