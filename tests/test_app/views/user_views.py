from typing import List

from django.contrib.auth.models import User
from ninja import Router

from ninja_crud import views
from ninja_crud.viewsets import ModelViewSet
from tests.test_app.schemas import UserIn, UserOut

router = Router()


class UserViewSet(ModelViewSet):
    model = User

    list_users = views.ListModelView(response_body=List[UserOut], pagination_class=None)
    create_user = views.CreateModelView(request_body=UserIn, response_body=UserOut)
    retrieve_user = views.RetrieveModelView(response_schema=UserOut)
    update_user = views.UpdateModelView(payload_schema=UserIn, response_schema=UserOut)
    delete_user = views.DeleteModelView()


UserViewSet.register_routes(router)
