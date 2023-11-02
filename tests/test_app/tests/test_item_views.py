import uuid

from ninja_crud.testing.core.components import (
    Headers,
    PathParameters,
    Payloads,
    QueryParameters,
)
from ninja_crud.testing.views import (
    DeleteModelViewTest,
    ListModelViewTest,
    RetrieveModelViewTest,
    UpdateModelViewTest,
)
from ninja_crud.testing.viewsets import ModelViewSetTestCase
from tests.test_app.tests.base_test_case import BaseTestCase
from tests.test_app.views.item_views import ItemViewSet


class TestItemViewSet(ModelViewSetTestCase, BaseTestCase):
    model_view_set_class = ItemViewSet
    base_path = "api/items"

    def get_path_parameters(self):
        return PathParameters(ok={"id": self.item_1.id}, not_found={"id": uuid.uuid4()})

    def get_headers_ok(self):
        return Headers(
            ok={"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"}, unauthorized={}
        )

    def get_headers_ok_forbidden(self):
        return Headers(
            ok={"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"},
            unauthorized={},
            forbidden={"HTTP_AUTHORIZATION": f"Bearer {self.user_2.id}"},
        )

    test_list_view = ListModelViewTest(
        headers=get_headers_ok,
        query_parameters=lambda self: QueryParameters(
            ok=[{}, {"order_by": ["name"], "limit": 1}]
        ),
    )
    test_retrieve_view = RetrieveModelViewTest(
        path_parameters=get_path_parameters,
        headers=get_headers_ok_forbidden,
    )
    test_update_view = UpdateModelViewTest(
        path_parameters=get_path_parameters,
        headers=get_headers_ok_forbidden,
        payloads=Payloads(
            ok={"name": "new-name", "description": "new-description"},
        ),
    )
    test_delete_view = DeleteModelViewTest(
        path_parameters=get_path_parameters, headers=get_headers_ok_forbidden
    )

    test_list_tags_view = ListModelViewTest(
        path_parameters=lambda self: PathParameters(ok={"id": self.item_1.id}),
        headers=get_headers_ok,
    )
