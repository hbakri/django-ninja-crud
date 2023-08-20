from functools import wraps
from uuid import UUID

from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from ninja import Router

from ninja_crud.views import (
    CreateModelView,
    DeleteModelView,
    ListModelView,
    ModelViewSet,
    PartialUpdateModelView,
    RetrieveModelView,
    UpdateModelView,
)
from tests.test_app.models import Collection, Item
from tests.test_app.schemas import (
    CollectionFilter,
    CollectionIn,
    CollectionOut,
    ItemIn,
    ItemOut,
)


def user_is_creator(func):
    @wraps(func)
    def wrapper(request: HttpRequest, id: UUID, *args, **kwargs):
        collection = Collection.objects.get(id=id)
        if collection.created_by != request.user:
            raise PermissionDenied()
        return func(request, id, *args, **kwargs)

    return wrapper


class CollectionViewSet(ModelViewSet):
    model_class = Collection
    input_schema = CollectionIn
    output_schema = CollectionOut
    filter_schema = CollectionFilter

    list = ListModelView(output_schema=output_schema, filter_schema=filter_schema)
    create = CreateModelView(
        input_schema=input_schema,
        output_schema=output_schema,
        instance_builder=lambda: Collection(),
        pre_save=lambda request, instance: setattr(
            instance, "created_by", request.user
        ),
        post_save=lambda request, instance: None,
    )
    retrieve = RetrieveModelView(output_schema=output_schema)
    update = UpdateModelView(
        input_schema=input_schema,
        output_schema=output_schema,
        decorators=[user_is_creator],
    )
    partial_update = PartialUpdateModelView(
        input_schema=input_schema,
        output_schema=output_schema,
        decorators=[user_is_creator],
    )
    delete = DeleteModelView(
        pre_delete=lambda request, id: None,
        post_delete=lambda request, id: None,
        decorators=[user_is_creator],
    )

    list_items = ListModelView(
        detail=True,
        queryset_getter=lambda id: Item.objects.filter(collection_id=id),
        output_schema=ItemOut,
        decorators=[user_is_creator],
    )
    create_item = CreateModelView(
        detail=True,
        instance_builder=lambda id: Item(collection_id=id),
        input_schema=ItemIn,
        output_schema=ItemOut,
        pre_save=lambda request, id, instance: None,
        post_save=lambda request, id, instance: None,
        decorators=[user_is_creator],
    )


router = Router()
CollectionViewSet.register_routes(router)
