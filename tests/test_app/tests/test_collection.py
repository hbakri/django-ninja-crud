import random
import uuid

from ninja_crud.tests import (
    AuthHeaders,
    CreateModelViewTest,
    DeleteModelViewTest,
    ListModelViewTest,
    ModelViewSetTest,
    PatchModelViewTest,
    PathParameters,
    Payloads,
    QueryParameters,
    RetrieveModelViewTest,
    UpdateModelViewTest,
)
from tests.test_app.tests.test_base import BaseTestCase
from tests.test_app.views.view_collection import CollectionViewSet


class CollectionViewSetTest(ModelViewSetTest, BaseTestCase):
    model_view_set_class = CollectionViewSet
    urls_prefix = "api/collections"

    def get_path_parameters(self):
        return PathParameters(
            ok=[{"id": self.collection_1.id}], not_found={"id": uuid.uuid4()}
        )

    def get_auth_headers_ok(self):
        return AuthHeaders(
            ok=[{"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"}], unauthorized={}
        )

    def get_auth_headers_ok_forbidden(self):
        return AuthHeaders(
            ok={"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"},
            unauthorized={"HTTP_AUTHORIZATION": f"Bearer {random.randint(100, 1000)}"},
            forbidden={"HTTP_AUTHORIZATION": f"Bearer {self.user_2.id}"},
        )

    collection_payloads = Payloads(
        ok={"name": "new-name", "description": "new-description"},
        bad_request={"name": []},
        conflict={"name": "collection-2"},
    )

    test_list = ListModelViewTest(
        auth_headers=get_auth_headers_ok,
        query_parameters=QueryParameters(
            ok=[{}, {"name": "collection-1", "order_by": ["name"], "limit": 1}],
            bad_request={"order_by": ["unknown_field"]},
        ),
    )
    test_create = CreateModelViewTest(
        auth_headers=get_auth_headers_ok,
        payloads=collection_payloads,
    )
    test_retrieve = RetrieveModelViewTest(
        path_parameters=get_path_parameters,
        auth_headers=get_auth_headers_ok,
    )
    test_update = UpdateModelViewTest(
        path_parameters=get_path_parameters,
        auth_headers=get_auth_headers_ok_forbidden,
        payloads=collection_payloads,
    )
    test_patch = PatchModelViewTest(
        path_parameters=get_path_parameters,
        auth_headers=get_auth_headers_ok_forbidden,
        payloads=Payloads(
            ok=[
                {"name": "new-name", "description": "new-description"},
                {"name": "new-name"},
                {"description": "new-description"},
            ],
            bad_request={"name": []},
            conflict={"name": "collection-2"},
        ),
    )
    test_delete = DeleteModelViewTest(
        path_parameters=get_path_parameters, auth_headers=get_auth_headers_ok_forbidden
    )

    test_list_items = ListModelViewTest(
        path_parameters=get_path_parameters, auth_headers=get_auth_headers_ok_forbidden
    )
    test_create_item = CreateModelViewTest(
        path_parameters=get_path_parameters,
        auth_headers=get_auth_headers_ok_forbidden,
        payloads=Payloads(
            ok={"name": "new-name", "description": "new-description"},
        ),
    )
