from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.core.dependencies import get_current_user
from app.db.database import get_db_session
from app.models.cars import Car
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/cars",
    tags=["Cars"],
    dependencies=[Depends(get_current_user)]  # protects ALL routes automatically
)


# Schemas
class CarResponse(BaseModel):
    id: int
    make: str
    model: str
    category: str | None
    year: int | None

    model_config = {"from_attributes": True}


class CarsListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    cars: list[CarResponse]


# Common pagination dependency
def pagination(skip: int = 0, limit: int = 20):
    return {"skip": skip, "limit": limit}


# Routes
@router.get("/", response_model=CarsListResponse)
def get_cars(
    db: Session = Depends(get_db_session),
    pages: dict = Depends(pagination)
):
    skip = pages["skip"]
    limit = pages["limit"]
    cars = db.query(Car).offset(skip).limit(limit).all()
    total = db.query(Car).count()
    return CarsListResponse(total=total, skip=skip, limit=limit, cars=cars)
