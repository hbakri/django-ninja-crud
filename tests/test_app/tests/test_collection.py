import random
import uuid

from ninja_crud.tests import (
    AuthParams,
    BodyParams,
    CreateModelViewTest,
    DeleteModelViewTest,
    ListModelViewTest,
    ModelViewSetTest,
    PathParams,
    QueryParams,
    RetrieveModelViewTest,
    UpdateModelViewTest,
)
from tests.test_app.tests.test_base import BaseTestCase
from tests.test_app.views.view_collection import CollectionViewSet


class CollectionViewSetTest(ModelViewSetTest, BaseTestCase):
    model_view_set = CollectionViewSet

    def get_path_params(self):
        return PathParams(
            ok={"id": self.collection_1.id}, not_found={"id": uuid.uuid4()}
        )

    def get_auth_params_ok(self):
        return AuthParams(
            ok={"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"}, unauthorized={}
        )

    def get_auth_params_ok_forbidden(self):
        return AuthParams(
            ok={"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"},
            unauthorized={"HTTP_AUTHORIZATION": f"Bearer {random.randint(100, 1000)}"},
            forbidden={"HTTP_AUTHORIZATION": f"Bearer {self.user_2.id}"},
        )

    collection_body_params = BodyParams(
        ok={"name": "new-name", "description": "new-description"},
        bad_request={"unknown_field": "unknown_field"},
        conflict={"name": "collection-2"},
    )

    test_list = ListModelViewTest(
        auth_params=get_auth_params_ok,
        query_params=QueryParams(
            ok={"name": "collection-1", "order_by": ["name"], "limit": 1},
            bad_request={"order_by": ["unknown_field"]},
        ),
    )
    test_create = CreateModelViewTest(
        auth_params=get_auth_params_ok,
        body_params=collection_body_params,
    )
    test_retrieve = RetrieveModelViewTest(
        path_params=get_path_params,
        auth_params=get_auth_params_ok,
    )
    test_update = UpdateModelViewTest(
        path_params=get_path_params,
        auth_params=get_auth_params_ok_forbidden,
        body_params=collection_body_params,
    )
    test_delete = DeleteModelViewTest(
        path_params=get_path_params, auth_params=get_auth_params_ok_forbidden
    )

    test_list_items = ListModelViewTest(
        path_params=get_path_params,
        auth_params=get_auth_params_ok_forbidden,
    )
    test_create_item = CreateModelViewTest(
        path_params=get_path_params,
        auth_params=get_auth_params_ok_forbidden,
        body_params=BodyParams(
            ok={"name": "new-name", "description": "new-description"},
        ),
    )
