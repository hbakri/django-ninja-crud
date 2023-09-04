from ninja_crud.tests import (
    CreateModelViewTest,
    PathParameters,
    Payloads,
    TestDeleteModelView,
    TestListModelView,
    TestModelViewSet,
    TestRetrieveModelView,
    TestUpdateModelView,
)
from tests.test_app.tests.test_base import BaseTestCase
from tests.test_app.views.view_user import UserViewSet


class TestUserViewSet(TestModelViewSet, BaseTestCase):
    model_view_set_class = UserViewSet
    base_path = "api/users"

    def get_path_parameters(self):
        return PathParameters(ok={"id": self.user_1.id})

    def get_user_payloads(self):
        return Payloads(
            ok={
                "username": "new-user",
                "email": "user@email.com",
                "password": "new-password",
            },
            bad_request={"username": "new-user", "password": "new-password"},
            conflict={
                "username": self.user_2.username,
                "email": "user@email.com",
                "password": "new-password",
            },
        )

    test_list = TestListModelView()
    test_create = CreateModelViewTest(payloads=get_user_payloads)
    test_retrieve = TestRetrieveModelView(path_parameters=get_path_parameters)
    test_update = TestUpdateModelView(
        path_parameters=get_path_parameters, payloads=get_user_payloads
    )
    test_delete = TestDeleteModelView(path_parameters=get_path_parameters)
