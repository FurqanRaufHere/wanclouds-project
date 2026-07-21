from pydantic import BaseModel

from app.common.schemas import get_pagination_schema


class CarResponse(BaseModel):
    id: str
    make: str
    model: str
    category: str | None
    year: int | None

    model_config = {"from_attributes": True}


class CarUpdateRequest(BaseModel):
    make: str | None = None
    model: str | None = None
    category: str | None = None
    year: int | None = None


CarsListResponse = get_pagination_schema(CarResponse)
