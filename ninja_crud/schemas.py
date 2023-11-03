from typing import List, Optional

from django.db.models import Q
from ninja import FilterSchema


class OrderableFilterSchema(FilterSchema):
    order_by: Optional[List[str]] = None

    def filter_order_by(self, value) -> Q:
        return Q()
