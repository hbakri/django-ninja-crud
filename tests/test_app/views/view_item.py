from functools import wraps
from uuid import UUID

from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from ninja import Router

from ninja_crud.views import (
    DeleteModelView,
    ListModelView,
    ModelViewSet,
    RetrieveModelView,
    UpdateModelView,
)
from tests.test_app.models import Item, Tag
from tests.test_app.schemas import ItemIn, ItemOut


def user_is_collection_creator(func):
    @wraps(func)
    def wrapper(request: HttpRequest, id: UUID, *args, **kwargs):
        item = Item.objects.get(id=id)
        if item.collection.created_by != request.user:
            raise PermissionDenied()
        return func(request, id, *args, **kwargs)

    return wrapper


class ItemViewSet(ModelViewSet):
    model = Item
    input_schema = ItemIn
    output_schema = ItemOut

    list = ListModelView(
        output_schema=output_schema,
        queryset_getter=lambda: Item.objects.get_queryset(),
    )
    retrieve = RetrieveModelView(
        output_schema=output_schema,
        queryset_getter=lambda id: Item.objects.get_queryset(),
        decorators=[user_is_collection_creator],
    )
    update = UpdateModelView(
        input_schema=input_schema,
        output_schema=output_schema,
        pre_save=lambda request, instance: None,
        post_save=lambda request, instance: None,
        decorators=[user_is_collection_creator],
    )
    delete = DeleteModelView(decorators=[user_is_collection_creator])

    list_tags = ListModelView(
        is_instance=True,
        related_model=Tag,
        output_schema=output_schema,
    )


router = Router()
ItemViewSet.register_routes(router)
