from django.contrib.auth.models import User
from ninja import Router

from ninja_crud.views import (
    CreateModelView,
    DeleteModelView,
    ListModelView,
    RetrieveModelView,
    UpdateModelView,
)
from ninja_crud.viewsets import ModelViewSet
from tests.test_app.schemas import UserIn, UserOut

router = Router()


class UserViewSet(ModelViewSet):
    model = User

    list_users = ListModelView(output_schema=UserOut, pagination_class=None)
    create_user = CreateModelView(input_schema=UserIn, output_schema=UserOut)
    retrieve_user = RetrieveModelView(output_schema=UserOut)
    update_user = UpdateModelView(input_schema=UserIn, output_schema=UserOut)
    delete_user = DeleteModelView()


UserViewSet.register_routes(router)
