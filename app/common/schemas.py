import math
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationQuerySchema(BaseModel):
    """Page-based pagination.

    Clients think in pages ("give me page 3"), not in row offsets, so that is
    what the query string exposes. The offset SQL needs is derived here rather
    than being the caller's problem.
    """

    page: int = Field(default=1, ge=1, description="1-based page number")
    limit: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic envelope for a page of results.

    Generic over the item type, so `PaginatedResponse[CarResponse]` is a real
    type that static checkers and OpenAPI both understand.
    """

    total: int
    page: int
    pages: int
    limit: int
    items: list[T]

    @classmethod
    def create(
        cls,
        items: list,
        total: int,
        pagination: PaginationQuerySchema,
    ) -> "PaginatedResponse[T]":
        return cls(
            total=total,
            page=pagination.page,
            pages=math.ceil(total / pagination.limit),
            limit=pagination.limit,
            items=items,
        )
