from typing import Any, Callable, TypeVar

from django.db.models import Model, QuerySet
from django.http import HttpRequest

ModelType = TypeVar("ModelType", bound=Model)
"""
Type alias for any instance of a Django Model.
This generic type is bound to Django's base Model class.
"""

DetailQuerySetGetter = Callable[[Any], QuerySet[ModelType]]
"""
Type hint for callables used in detail views where the intention is to retrieve a QuerySet for a single entity.

Expected signature: (id: Any) -> QuerySet[Model]
"""

CollectionQuerySetGetter = Callable[[], QuerySet[ModelType]]
"""
Type hint for callables used in collection views where the intention is to retrieve a QuerySet for a collection.

Expected signature: () -> QuerySet[Model]
"""

DetailInstanceBuilder = Callable[[Any], ModelType]
"""
Type hint for callables used in detail views where the intention is to build an instance of a single entity.

Expected signature: (id: Any) -> Model
"""

CollectionInstanceBuilder = Callable[[], ModelType]
"""
Type hint for callables used in collection views where the intention is to build an instance of a single entity.

Expected signature: () -> Model
"""

CreateDetailSaveHook = Callable[[HttpRequest, Any, ModelType], None]
"""
Type hint for callables used in detail views during a create action where the intention is to
perform a save operation for a single entity.

Expected signature: (request: HttpRequest, id: Any, instance: Model) -> None
"""

CreateCollectionSaveHook = Callable[[HttpRequest, ModelType], None]
"""
Type hint for callables used in collection views during a create action where the intention is to
perform a pre/post save operation over the created entity.

Expected signature: (request: HttpRequest, instance: Model) -> None
"""
