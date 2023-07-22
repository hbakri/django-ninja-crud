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


class UserViewSet(ModelViewSet):
    model_class = User
    input_schema = UserIn
    output_schema = UserOut

    list = ListModelView(output_schema=output_schema)
    create = CreateModelView(input_schema=input_schema, output_schema=output_schema)
    retrieve = RetrieveModelView(output_schema=output_schema)
    update = UpdateModelView(input_schema=input_schema, output_schema=output_schema)
    delete = DeleteModelView()


router = Router()
UserViewSet.register_routes(router)
