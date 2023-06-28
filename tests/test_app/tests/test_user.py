import random

from ninja_crud.tests import (
    BodyParams,
    CreateModelViewTest,
    DeleteModelViewTest,
    ListModelViewTest,
    ModelViewSetTest,
    PathParams,
    RetrieveModelViewTest,
    UpdateModelViewTest,
)
from tests.test_app.tests.test_base import BaseTestCase
from tests.test_app.views.view_user import UserViewSet


class UserViewSetTest(ModelViewSetTest, BaseTestCase):
    model_view_set = UserViewSet

    def get_path_params(self):
        return PathParams(
            ok={"id": self.user_1.id}, not_found={"id": random.randint(1000, 9999)}
        )

    user_body_params = BodyParams(
        ok={
            "username": "new-user",
            "email": "user@email.com",
            "password": "new-password",
        },
        bad_request={"username": "new-user", "password": "new-password"},
        conflict={
            "username": "user-2",
            "email": "user@email.com",
            "password": "new-password",
        },
    )

    test_list = ListModelViewTest()
    test_create = CreateModelViewTest(body_params=user_body_params)
    test_retrieve = RetrieveModelViewTest(path_params=get_path_params)
    test_update = UpdateModelViewTest(
        path_params=get_path_params, body_params=user_body_params
    )
    test_delete = DeleteModelViewTest(path_params=get_path_params)
