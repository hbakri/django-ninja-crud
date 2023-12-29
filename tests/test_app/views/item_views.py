from functools import wraps

from django.core.exceptions import PermissionDenied
from ninja import Router

from ninja_crud.schemas import OrderByFilterSchema
from ninja_crud.views import (
    DeleteModelView,
    ListModelView,
    RetrieveModelView,
    UpdateModelView,
)
from ninja_crud.viewsets import ModelViewSet
from tests.test_app.models import Item, Tag
from tests.test_app.schemas import ItemIn, ItemOut, TagOut

router = Router()


def user_is_collection_creator(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        item_id = kwargs.get("id")
        item = Item.objects.get(id=item_id)
        if item.collection.created_by != request.auth:
            raise PermissionDenied()
        return func(request, *args, **kwargs)

    return wrapper


class ItemViewSet(ModelViewSet):
    model = Item
    default_input_schema = ItemIn
    default_output_schema = ItemOut

    list_items = ListModelView(
        filter_schema=OrderByFilterSchema,
        queryset_getter=lambda: Item.objects.get_queryset(),
    )
    retrieve_item = RetrieveModelView(
        queryset_getter=lambda id: Item.objects.get_queryset(),
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
        queryset_getter=lambda id: Tag.objects.filter(items__id=id),
        output_schema=TagOut,
    )


ItemViewSet.register_routes(router)
