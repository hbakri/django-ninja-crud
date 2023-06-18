from typing import Optional
from uuid import UUID

from ninja import Schema

from ninja_crud.schemas import OrderableFilterSchema


class Identifiable(Schema):
    id: UUID


class Representable(Schema):
    name: str
    description: str = None


class CollectionFilter(OrderableFilterSchema):
    name: Optional[str]


class CollectionIn(Representable):
    pass


class CollectionOut(Identifiable, Representable):
    pass


class ItemIn(Representable):
    pass


class ItemOut(Identifiable, Representable):
    collection_id: UUID
