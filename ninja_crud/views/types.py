from typing import Any, Callable, TypeVar

from django.db.models import Model, QuerySet

ModelType = TypeVar("ModelType", bound=Model)
"""
Type alias for any instance of a Django Model.
This generic type is bound to Django's base Model class.
"""

DetailQuerySetGetter = Callable[[Any], QuerySet[ModelType]]
"""
Type hint for callables used in detail views where the intention is to retrieve a QuerySet for a single entity.

This type is especially used in contexts where a `detail=True` flag indicates that the view is intended
to fetch details for an individual object rather than a collection.

Expected signature: (id: Any) -> QuerySet[Model]
"""

CollectionQuerySetGetter = Callable[[], QuerySet[ModelType]]
"""
Type hint for callables used in collection views where the intention is to retrieve a QuerySet for a collection.

This type is especially used in contexts where a `detail=False` flag indicates that the view is intended
to fetch a collection of objects rather than a single object.

Expected signature: () -> QuerySet[Model]
"""
