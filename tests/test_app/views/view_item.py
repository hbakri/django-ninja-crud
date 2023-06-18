from ninja import Router

from ninja_crud.views import (
    DeleteModelView,
    ModelViewSet,
    RetrieveModelView,
    UpdateModelView,
)
from tests.test_app.models import Item
from tests.test_app.schemas import ItemIn, ItemOut


class ItemViewSet(ModelViewSet):
    model = Item
    input_schema = ItemIn
    output_schema = ItemOut

    retrieve = RetrieveModelView(
        output_schema=output_schema,
        queryset_getter=lambda id: Item.objects.select_related("collection"),
    )
    update = UpdateModelView(
        input_schema=input_schema,
        output_schema=output_schema,
        pre_save=lambda request, instance: None,
        post_save=lambda request, instance: None,
    )
    delete = DeleteModelView()


router = Router()
ItemViewSet.register_routes(router)
