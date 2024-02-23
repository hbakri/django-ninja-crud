from typing import List, Optional
from uuid import UUID

from django.db.models import Q, QuerySet
from ninja import FilterSchema, Schema


class Identifiable(Schema):
    id: UUID


class Representable(Schema):
    name: str
    description: Optional[str] = None


class OrderByFilterSchema(FilterSchema):
    order_by: Optional[List[str]] = None

    def filter_order_by(self, value) -> Q:
        return Q()

    def filter(self, queryset: QuerySet) -> QuerySet:
        queryset = super().filter(queryset)
        if self.order_by:
            queryset = queryset.order_by(*self.order_by)
        return queryset


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


class UserRequestBody(Schema):
    username: str
    email: str
    password: str
    groups: Optional[List[int]] = None


class UserResponseBody(Schema):
    id: int
    username: str
    email: str


class UserQueryParameters(Schema):
    username__contains: Optional[str] = None
