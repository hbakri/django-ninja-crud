from typing import List, Optional

from django.db.models import Q, QuerySet
from ninja import FilterSchema


class OrderByFilterSchema(FilterSchema):
    order_by: Optional[List[str]] = None

    def filter_order_by(self, value) -> Q:
        return Q()

    def filter(self, queryset: QuerySet) -> QuerySet:
        queryset = super().filter(queryset)
        if self.order_by:
            queryset = queryset.order_by(*self.order_by)
        return queryset
