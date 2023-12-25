import random
import uuid

from ninja_crud.testing.core.components import (
    Headers,
    PathParameters,
    Payloads,
    QueryParameters,
)
from ninja_crud.testing.views import (
    CreateModelViewTest,
    DeleteModelViewTest,
    ListModelViewTest,
    RetrieveModelViewTest,
    UpdateModelViewTest,
)
from ninja_crud.testing.viewsets import ModelViewSetTestCase
from tests.test_app.tests.base_test_case import BaseTestCase
from tests.test_app.views.collection_views import CollectionViewSet


class TestCollectionViewSet(ModelViewSetTestCase, BaseTestCase):
    model_viewset_class = CollectionViewSet
    base_path = "api/collections"

    def get_path_parameters(self):
        return PathParameters(
            ok=[{"id": self.collection_1.id}], not_found={"id": uuid.uuid4()}
        )

    def get_headers_ok(self):
        return Headers(
            ok=[{"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"}], unauthorized={}
        )

    def get_headers_ok_forbidden(self):
        return Headers(
            ok={"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"},
            unauthorized={"HTTP_AUTHORIZATION": f"Bearer {random.randint(100, 1000)}"},
            forbidden={"HTTP_AUTHORIZATION": f"Bearer {self.user_2.id}"},
        )

    collection_payloads = Payloads(
        ok={"name": "new-name", "description": "new-description"},
        bad_request={"name": []},
        conflict={"name": "collection-2"},
    )

    test_list_collections = ListModelViewTest(
        headers=get_headers_ok,
        query_parameters=QueryParameters(
            ok=[{}, {"name": "collection-1", "order_by": ["name"], "limit": 1}],
            bad_request={"order_by": ["unknown_field"]},
        ),
    )
    test_create_collection = CreateModelViewTest(
        headers=get_headers_ok,
        payloads=collection_payloads,
    )
    test_retrieve_collection = RetrieveModelViewTest(
        path_parameters=get_path_parameters,
        headers=get_headers_ok,
    )
    test_update_collection = UpdateModelViewTest(
        path_parameters=get_path_parameters,
        headers=get_headers_ok_forbidden,
        payloads=collection_payloads,
    )
    test_delete_collection = DeleteModelViewTest(
        path_parameters=get_path_parameters, headers=get_headers_ok_forbidden
    )

    test_list_collection_items = ListModelViewTest(
        path_parameters=get_path_parameters, headers=get_headers_ok_forbidden
    )
    test_create_collection_item = CreateModelViewTest(
        path_parameters=get_path_parameters,
        headers=get_headers_ok_forbidden,
        payloads=Payloads(
            ok={"name": "new-name", "description": "new-description"},
        ),
    )
