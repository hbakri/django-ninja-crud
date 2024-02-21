from functools import wraps
from typing import List

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
        collection_id = getattr(kwargs.get("path_parameters"), "id", None)
        collection = Collection.objects.get(id=collection_id)
        if collection.created_by != request.auth:
            raise PermissionDenied()
        return func(request, *args, **kwargs)

    return wrapper


class CollectionViewSet(ModelViewSet):
    model = Collection

    list_collections = ListModelView(
        response_body=List[CollectionOut], query_parameters=CollectionFilter
    )
    create_collection = CreateModelView(
        request_body=CollectionIn,
        response_body=CollectionOut,
        create_model=lambda request, path_parameters: Collection(
            created_by=request.auth
        ),
        pre_save=lambda request, path_parameters, instance: instance.full_clean(),
        post_save=lambda request, path_parameters, instance: None,
    )
    retrieve_collection = RetrieveModelView(response_body=CollectionOut)
    update_collection = UpdateModelView(
        request_body=CollectionIn,
        response_body=CollectionOut,
        decorators=[user_is_creator],
    )
    delete_collection = DeleteModelView(
        pre_delete=lambda request, path_parameters, instance: None,
        post_delete=lambda request, path_parameters, instance: None,
        decorators=[user_is_creator],
    )

    list_collection_items = ListModelView(
        path="/{id}/items/",
        get_queryset=lambda path_parameters: Item.objects.filter(
            collection_id=getattr(path_parameters, "id", None)
        ),
        response_body=List[ItemOut],
        decorators=[user_is_creator],
    )
    create_collection_item = CreateModelView(
        path="/{id}/items/",
        create_model=lambda request, path_parameters: Item(
            collection_id=getattr(path_parameters, "id", None)
        ),
        request_body=ItemIn,
        response_body=ItemOut,
        pre_save=lambda request, path_parameters, instance: instance.full_clean(),
        post_save=lambda request, path_parameters, instance: None,
        decorators=[user_is_creator],
    )


CollectionViewSet.register_routes(router)
