from typing import Optional
from uuid import UUID

from ninja import Schema

from ninja_crud.schemas import OrderByFilterSchema


class Identifiable(Schema):
    id: UUID


class Representable(Schema):
    name: str
    description: Optional[str] = None


class CollectionFilter(OrderByFilterSchema):
    name: Optional[str] = None


class CollectionIn(Representable):
    pass


class CollectionOut(Identifiable, Representable):
    pass


class ItemIn(Representable):
    pass


class ItemOut(Identifiable, Representable):
    collection_id: UUID


class TagOut(Identifiable, Representable):
    pass


class UserIn(Schema):
    username: str
    email: str
    password: str


class UserOut(Schema):
    id: int
    username: str
    email: str
