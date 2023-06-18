from uuid import UUID

from ninja import Schema


class Identifiable(Schema):
    id: UUID


class Representable(Schema):
    name: str
    description: str = None


class CollectionIn(Representable):
    pass


class CollectionOut(Identifiable, Representable):
    pass


class ItemIn(Representable):
    pass


class ItemOut(Identifiable, Representable):
    collection_id: UUID
