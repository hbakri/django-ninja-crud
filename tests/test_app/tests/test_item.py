import uuid
from typing import Union

from django.test import TestCase

from ninja_crud.tests import (
    AuthParams,
    BodyParams,
    DeleteModelViewTest,
    ListModelViewTest,
    ModelViewSetTest,
    PathParams,
    RetrieveModelViewTest,
    UpdateModelViewTest,
)
from tests.test_app.tests.test_base import BaseTestCase
from tests.test_app.views.view_item import ItemViewSet


class ItemViewSetTest(ModelViewSetTest, BaseTestCase):
    model_view_set = ItemViewSet

    def get_path_params(self):
        return PathParams(ok={"id": self.item_1.id}, not_found={"id": uuid.uuid4()})

    def get_auth_params_ok(self: Union["ItemViewSetTest", TestCase]):
        return AuthParams(
            ok={"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"}, unauthorized={}
        )

    def get_auth_params_ok_forbidden(self: Union["ItemViewSetTest", TestCase]):
        return AuthParams(
            ok={"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"},
            unauthorized={},
            forbidden={"HTTP_AUTHORIZATION": f"Bearer {self.user_2.id}"},
        )

    item_body_params = BodyParams(
        ok={"name": "new-name", "description": "new-description"},
    )

    test_list = ListModelViewTest(
        auth_params=get_auth_params_ok,
    )
    test_retrieve = RetrieveModelViewTest(
        path_params=get_path_params,
        auth_params=get_auth_params_ok_forbidden,
    )
    test_update = UpdateModelViewTest(
        path_params=get_path_params,
        auth_params=get_auth_params_ok_forbidden,
        body_params=item_body_params,
    )
    test_delete = DeleteModelViewTest(
        path_params=get_path_params, auth_params=get_auth_params_ok_forbidden
    )

    test_list_tags = ListModelViewTest(
        path_params=lambda self: PathParams(ok={"id": self.item_1.id}),
        auth_params=get_auth_params_ok,
    )
