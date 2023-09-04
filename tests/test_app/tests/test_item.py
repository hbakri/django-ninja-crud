import uuid

from ninja_crud.tests import (
    AuthHeaders,
    ListModelViewTest,
    PathParameters,
    Payloads,
    QueryParameters,
    TestDeleteModelView,
    TestModelViewSet,
    TestRetrieveModelView,
    TestUpdateModelView,
)
from tests.test_app.tests.test_base import BaseTestCase
from tests.test_app.views.view_item import ItemViewSet


class TestItemViewSet(TestModelViewSet, BaseTestCase):
    model_view_set_class = ItemViewSet
    base_path = "api/items"

    def get_path_parameters(self):
        return PathParameters(ok={"id": self.item_1.id}, not_found={"id": uuid.uuid4()})

    def get_auth_headers_ok(self):
        return AuthHeaders(
            ok={"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"}, unauthorized={}
        )

    def get_auth_headers_ok_forbidden(self):
        return AuthHeaders(
            ok={"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"},
            unauthorized={},
            forbidden={"HTTP_AUTHORIZATION": f"Bearer {self.user_2.id}"},
        )

    test_list = ListModelViewTest(
        auth_headers=get_auth_headers_ok,
        query_parameters=lambda self: QueryParameters(
            ok=[{}, {"order_by": ["name"], "limit": 1}]
        ),
    )
    test_retrieve = TestRetrieveModelView(
        path_parameters=get_path_parameters,
        auth_headers=get_auth_headers_ok_forbidden,
    )
    test_update = TestUpdateModelView(
        path_parameters=get_path_parameters,
        auth_headers=get_auth_headers_ok_forbidden,
        payloads=Payloads(
            ok={"name": "new-name", "description": "new-description"},
        ),
    )
    test_delete = TestDeleteModelView(
        path_parameters=get_path_parameters, auth_headers=get_auth_headers_ok_forbidden
    )

    test_list_tags = ListModelViewTest(
        path_parameters=lambda self: PathParameters(ok={"id": self.item_1.id}),
        auth_headers=get_auth_headers_ok,
    )
