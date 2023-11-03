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
Alias for a callable expected to retrieve a QuerySet for a detail view.

Parameters:
    id (Any): The identifier of the detail instance.

Returns:
    QuerySet[ModelType]: The QuerySet of model instances.
"""

CollectionQuerySetGetter = Callable[[], QuerySet[ModelType]]
"""
Alias for a callable expected to retrieve a QuerySet for a collection view.

Parameters:
    None

Returns:
    QuerySet[ModelType]: The QuerySet of model instances.
"""

DetailModelFactory = Callable[[Any], ModelType]
"""
Alias for a callable that returns a new instance for a detail view.

Parameters:
    id (Any): The identifier of the detail instance.

Returns:
    ModelType: The instance of the model that was created.
"""

CollectionModelFactory = Callable[[], ModelType]
"""
Alias for a callable that returns a new instance for a collection view.

Parameters:
    None

Returns:
    ModelType: The instance of the model that was created.
"""

CreateDetailSaveHook = Callable[[HttpRequest, Any, ModelType], None]
"""
Alias for a callback/hook executed during a create operation on a detail view.

Parameters:
    request (HttpRequest): The request object associated with the create operation.
    id (Any): The identifier of the detail instance.
    instance (ModelType): The instance of the model that was created.
"""

CreateCollectionSaveHook = Callable[[HttpRequest, ModelType], None]
"""
Alias for a callback/hook executed during a create operation on a collection view.

Parameters:
    request (HttpRequest): The request object associated with the create operation.
    instance (ModelType): The instance of the model that was created.
"""

UpdateSaveHook = Callable[[HttpRequest, ModelType, ModelType], None]
"""
Alias for a callback/hook executed during an update operation.

Parameters:
    request (HttpRequest): The request object associated with the update operation.
    old_instance (ModelType): The instance of the model before the update.
    new_instance (ModelType): The instance of the model after the update.
"""

PreDeleteHook = Callable[[HttpRequest, ModelType], None]
"""
Alias for a callback/hook executed prior to a model deletion.

Parameters:
    request (HttpRequest): The request object associated with the delete operation.
    instance (ModelType): The instance of the model that is about to be deleted.
"""

PostDeleteHook = Callable[[HttpRequest, Any, ModelType], None]
"""
Alias for a callback/hook executed after a model deletion.

Parameters:
    request (HttpRequest): The request object associated with the delete operation.
    id (Any): The identifier of the deleted instance.
    deleted_instance (ModelType): The instance of the model that was deleted from the database.

Note:
    Be cautious when using `deleted_instance` as the object no longer resides in the database.
"""
