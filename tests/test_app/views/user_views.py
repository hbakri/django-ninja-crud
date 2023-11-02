from django.contrib.auth.models import User
from ninja import Router

from ninja_crud.views import (
    CreateModelView,
    DeleteModelView,
    ListModelView,
    ModelViewSet,
    RetrieveModelView,
    UpdateModelView,
)
from tests.test_app.schemas import UserIn, UserOut

router = Router()


class UserViewSet(ModelViewSet):
    model_class = User
    input_schema = UserIn
    output_schema = UserOut

    list_view = ListModelView(output_schema=output_schema, pagination_class=None)
    create_view = CreateModelView(
        input_schema=input_schema, output_schema=output_schema
    )
    retrieve_view = RetrieveModelView(output_schema=output_schema)
    update_view = UpdateModelView(
        input_schema=input_schema, output_schema=output_schema
    )
    delete_view = DeleteModelView()


UserViewSet.register_routes(router)
