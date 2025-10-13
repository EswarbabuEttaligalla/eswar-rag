from pydantic import BaseModel


class PaginatedResponse(BaseModel):
    total: int
    items: list
