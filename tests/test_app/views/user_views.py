from typing import List

from django.contrib.auth.models import User
from ninja import Router

from ninja_crud import views
from ninja_crud.viewsets import ModelViewSet
from tests.test_app.schemas import (
    UserQueryParameters,
    UserRequestBody,
    UserResponseBody,
)

router = Router()


class UserViewSet(ModelViewSet):
    model = User

    list_users = views.ListModelView(
        query_parameters=UserQueryParameters,
        response_body=List[UserResponseBody],
        pagination_class=None,
    )
    create_user = views.CreateModelView(
        request_body=UserRequestBody, response_body=UserResponseBody
    )
    retrieve_user = views.RetrieveModelView(response_body=UserResponseBody)
    update_user = views.UpdateModelView(
        request_body=UserRequestBody, response_body=UserResponseBody
    )
    delete_user = views.DeleteModelView()


UserViewSet.register_routes(router)
