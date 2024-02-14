from functools import wraps
from typing import List

from django.core.exceptions import PermissionDenied
from ninja import Router

from ninja_crud.views import (
    DeleteModelView,
    ListModelView,
    RetrieveModelView,
    UpdateModelView,
)
from ninja_crud.viewsets import ModelViewSet
from tests.test_app.models import Item, Tag
from tests.test_app.schemas import ItemIn, ItemOut, OrderByFilterSchema, TagOut

router = Router()


def user_is_collection_creator(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        item_id = kwargs.get("path_parameters").id
        item = Item.objects.get(id=item_id)
        if item.collection.created_by != request.auth:
            raise PermissionDenied()
        return func(request, *args, **kwargs)

    return wrapper


class ItemViewSet(ModelViewSet):
    model = Item
    default_request_body = ItemIn
    default_response_body = ItemOut

    list_items = ListModelView(
        query_parameters=OrderByFilterSchema,
        get_queryset=lambda path_parameters: Item.objects.get_queryset(),
    )
    retrieve_item = RetrieveModelView(
        get_model=lambda path_parameters: Item.objects.get(id=path_parameters.id),
        decorators=[user_is_collection_creator],
    )
    update_item = UpdateModelView(
        pre_save=lambda request, old_instance, new_instance: None,
        post_save=lambda request, old_instance, new_instance: None,
        decorators=[user_is_collection_creator],
    )
    delete_item = DeleteModelView(decorators=[user_is_collection_creator])

    list_tags = ListModelView(
        path="/{id}/tags/",
        get_queryset=lambda path_parameters: Tag.objects.filter(
            items__id=path_parameters.id
        ),
        response_body=List[TagOut],
    )


ItemViewSet.register_routes(router)
