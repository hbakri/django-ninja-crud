from typing import Generic, Optional, TypeVar
from uuid import UUID

from django.db.models import Q, QuerySet
from ninja import FilterSchema, Schema


class Identifiable(Schema):
    id: UUID


class Representable(Schema):
    name: str
    description: Optional[str] = None


class OrderByFilter(FilterSchema):
    order_by: Optional[list[str]] = None

    def filter_order_by(self, value) -> Q:
        return Q()

    def filter(self, queryset: QuerySet) -> QuerySet:
        queryset = super().filter(queryset)
        if self.order_by:
            queryset = queryset.order_by(*self.order_by)
        return queryset


class CollectionFilter(OrderByFilter):
    name: Optional[str] = None


class CollectionIn(Representable):
    pass


class CollectionOut(Identifiable, Representable):
    pass


class ItemIn(Representable):
    pass


class ItemOut(Identifiable, Representable):
    collection_id: UUID


class ItemFilter(OrderByFilter):
    name: Optional[str] = None


class TagOut(Identifiable, Representable):
    pass


class UserRequestBody(Schema):
    username: str
    email: str
    password: str
    groups: Optional[list[int]] = None


class UserResponseBody(Schema):
    id: int
    username: str
    email: str


class UserQueryParameters(Schema):
    username__contains: Optional[str] = None


T = TypeVar("T")


class Paged(Schema, Generic[T]):
    items: list[T]
    count: int
