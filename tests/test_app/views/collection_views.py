from functools import wraps

from django.core.exceptions import PermissionDenied
from ninja import Router

from ninja_crud.views import (
    CreateModelView,
    DeleteModelView,
    ListModelView,
    RetrieveModelView,
    UpdateModelView,
)
from ninja_crud.viewsets import ModelViewSet
from tests.test_app.models import Collection, Item
from tests.test_app.schemas import (
    CollectionFilter,
    CollectionIn,
    CollectionOut,
    ItemIn,
    ItemOut,
)

router = Router()


def user_is_creator(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        collection_id = kwargs.get("id")
        collection = Collection.objects.get(id=collection_id)
        if collection.created_by != request.auth:
            raise PermissionDenied()
        return func(request, *args, **kwargs)

    return wrapper


class CollectionViewSet(ModelViewSet):
    model = Collection

    list_collections = ListModelView(
        response_schema=CollectionOut, filter_schema=CollectionFilter
    )
    create_collection = CreateModelView(
        input_schema=CollectionIn,
        response_schema=CollectionOut,
        model_factory=lambda: Collection(),
        pre_save=lambda request, instance: setattr(
            instance, "created_by", request.auth
        ),
        post_save=lambda request, instance: None,
    )
    retrieve_collection = RetrieveModelView(response_schema=CollectionOut)
    update_collection = UpdateModelView(
        input_schema=CollectionIn,
        response_schema=CollectionOut,
        decorators=[user_is_creator],
    )
    delete_collection = DeleteModelView(
        pre_delete=lambda request, instance: None,
        post_delete=lambda request, id, deleted_instance: None,
        decorators=[user_is_creator],
    )

    list_collection_items = ListModelView(
        path="/{id}/items/",
        queryset_getter=lambda id: Item.objects.filter(collection_id=id),
        response_schema=ItemOut,
        decorators=[user_is_creator],
    )
    create_collection_item = CreateModelView(
        path="/{id}/items/",
        model_factory=lambda id: Item(collection_id=id),
        input_schema=ItemIn,
        response_schema=ItemOut,
        pre_save=lambda request, id, instance: None,
        post_save=lambda request, id, instance: None,
        decorators=[user_is_creator],
    )


CollectionViewSet.register_routes(router)
