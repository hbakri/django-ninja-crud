from django.contrib.auth.models import User
from ninja import Router

from ninja_crud import views
from ninja_crud.viewsets import APIViewSet
from tests.test_app.schemas import (
    UserQueryParameters,
    UserRequestBody,
    UserResponseBody,
)

router = Router()


class UserViewSet(APIViewSet):
    model = User

    list_users = views.ListView(
        query_parameters=UserQueryParameters,
        response_body=list[UserResponseBody],
        pagination_class=None,
    )
    create_user = views.CreateView(
        request_body=UserRequestBody, response_body=UserResponseBody
    )
    read_user = views.ReadView(response_body=UserResponseBody)
    update_user = views.UpdateView(
        request_body=UserRequestBody, response_body=UserResponseBody
    )
    delete_user = views.DeleteView()


UserViewSet.add_views_to(router)
