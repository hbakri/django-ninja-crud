from functools import wraps

from django.core.exceptions import PermissionDenied
from ninja import Router

from ninja_crud import views
from ninja_crud.viewsets import APIViewSet
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


class CollectionViewSet(APIViewSet):
    model = Collection

    list_collections = views.ListView(
        response_body=list[CollectionOut], query_parameters=CollectionFilter
    )
    create_collection = views.CreateView(
        request_body=CollectionIn,
        response_body=CollectionOut,
        init_model=lambda request, path_parameters: Collection(created_by=request.auth),
        pre_save=lambda request, instance: instance.full_clean(),
        post_save=lambda request, instance: None,
    )
    read_collection = views.ReadView(response_body=CollectionOut)
    update_collection = views.UpdateView(
        request_body=CollectionIn,
        response_body=CollectionOut,
        decorators=[user_is_creator],
    )
    delete_collection = views.DeleteView(
        pre_delete=lambda request, instance: None,
        post_delete=lambda request, instance: None,
        decorators=[user_is_creator],
    )

    list_collection_items = views.ListView(
        path="/{id}/items/",
        get_queryset=lambda request, path_parameters: Item.objects.filter(
            collection_id=path_parameters.id
        ),
        response_body=list[ItemOut],
        decorators=[user_is_creator],
    )
    create_collection_item = views.CreateView(
        path="/{id}/items/",
        init_model=lambda request, path_parameters: Item(
            collection_id=path_parameters.id
        ),
        request_body=ItemIn,
        response_body=ItemOut,
        pre_save=lambda request, instance: instance.full_clean(),
        post_save=lambda request, instance: None,
        decorators=[user_is_creator],
    )


CollectionViewSet.add_views_to(router)
