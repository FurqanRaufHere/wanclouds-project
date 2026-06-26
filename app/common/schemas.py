from typing import TypeVar

from pydantic import BaseModel, Field, create_model

T = TypeVar("T")


class PaginationQuerySchema(BaseModel):
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


def get_pagination_schema(item_schema: type[T]) -> type[BaseModel]:
    return create_model(
        f"Paginated{item_schema.__name__}",
        total=(int, ...),
        skip=(int, ...),
        limit=(int, ...),
        items=(list[item_schema], ...),
    )
