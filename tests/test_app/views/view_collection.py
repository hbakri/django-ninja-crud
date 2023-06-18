from ninja import Router

from ninja_crud.views import (
    CreateModelView,
    DeleteModelView,
    ListModelView,
    ModelViewSet,
    RetrieveModelView,
    UpdateModelView,
)
from tests.test_app.models import Collection, Item
from tests.test_app.schemas import CollectionIn, CollectionOut, ItemIn, ItemOut


class CollectionViewSet(ModelViewSet):
    model = Collection
    input_schema = CollectionIn
    output_schema = CollectionOut

    list = ListModelView(output_schema=output_schema)
    create = CreateModelView(
        input_schema=input_schema,
        output_schema=output_schema,
        pre_save=lambda request, instance: None,
        post_save=lambda request, instance: None,
    )
    retrieve = RetrieveModelView(output_schema=output_schema)
    update = UpdateModelView(input_schema=input_schema, output_schema=output_schema)
    delete = DeleteModelView()

    list_items = ListModelView(
        is_instance_view=True,
        related_model=Item,
        output_schema=ItemOut,
        queryset_getter=lambda id: Item.objects.filter(collection_id=id),
    )
    create_item = CreateModelView(
        is_instance_view=True,
        related_model=Item,
        input_schema=ItemIn,
        output_schema=ItemOut,
        pre_save=lambda request, id, instance: setattr(instance, "collection_id", id),
        post_save=lambda request, id, instance: None,
    )


router = Router()
CollectionViewSet.register_routes(router)
