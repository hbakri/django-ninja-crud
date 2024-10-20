from typing import Generic, TypeVar
from uuid import UUID

from django.db.models import Q, QuerySet
from ninja import FilterSchema, Schema


class Identifiable(Schema):
    id: UUID


class Representable(Schema):
    name: str
    description: str | None = None


class OrderByFilter(FilterSchema):
    order_by: list[str] | None = None

    def filter_order_by(self, value) -> Q:
        return Q()

    def filter(self, queryset: QuerySet) -> QuerySet:
        queryset = super().filter(queryset)
        if self.order_by:
            queryset = queryset.order_by(*self.order_by)
        return queryset


class CollectionFilter(OrderByFilter):
    name: str | None = None


class CollectionIn(Representable):
    pass


class CollectionOut(Identifiable, Representable):
    pass


class ItemIn(Representable):
    pass


class ItemOut(Identifiable, Representable):
    collection_id: UUID


class ItemFilter(OrderByFilter):
    name: str | None = None


class TagOut(Identifiable, Representable):
    pass


class UserRequestBody(Schema):
    username: str
    email: str
    password: str
    groups: list[int] | None = None


class UserResponseBody(Schema):
    id: int
    username: str
    email: str


class UserQueryParameters(Schema):
    username__contains: str | None = None


T = TypeVar("T")


class Paged(Schema, Generic[T]):
    items: list[T]
    count: int
