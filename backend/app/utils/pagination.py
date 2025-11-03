from typing import Iterable, TypeVar

T = TypeVar("T")


def paginate(items: Iterable[T], offset: int = 0, limit: int = 50) -> list[T]:
    return list(items)[offset : offset + limit]
