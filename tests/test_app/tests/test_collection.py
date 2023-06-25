import random
from typing import Union

from django.test import TestCase

from ninja_crud.tests import (
    CreateModelViewTest,
    Credentials,
    DeleteModelViewTest,
    ListModelViewTest,
    ModelViewSetTest,
    Payloads,
    RetrieveModelViewTest,
    UpdateModelViewTest,
)
from tests.test_app.tests.test_base import BaseTestCase
from tests.test_app.views.view_collection import CollectionViewSet


class CollectionViewSetTest(ModelViewSetTest, BaseTestCase):
    model_view_set = CollectionViewSet

    def get_instance(self: Union["CollectionViewSetTest", TestCase]):
        return self.collection_1

    def get_credentials_ok(self: Union["CollectionViewSetTest", TestCase]):
        return Credentials(
            ok={"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"}, unauthorized={}
        )

    def get_credentials_ok_forbidden(self: Union["CollectionViewSetTest", TestCase]):
        return Credentials(
            ok={"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"},
            unauthorized={"HTTP_AUTHORIZATION": f"Bearer {random.randint(100, 1000)}"},
            forbidden={"HTTP_AUTHORIZATION": f"Bearer {self.user_2.id}"},
        )

    collection_payloads = Payloads(
        ok={"name": "new-name", "description": "new-description"},
        bad_request={"unknown_field": "unknown_field"},
        conflict={"name": "collection-2"},
    )

    test_list = ListModelViewTest(
        instance_getter=get_instance,
        credentials_getter=get_credentials_ok,
        filters=Payloads(
            ok={"name": "collection-1", "order_by": ["name"], "limit": 1},
            bad_request={"order_by": ["unknown_field"]},
        ),
    )
    test_create = CreateModelViewTest(
        payloads=collection_payloads,
        instance_getter=get_instance,
        credentials_getter=get_credentials_ok,
    )
    test_retrieve = RetrieveModelViewTest(
        instance_getter=get_instance,
        credentials_getter=get_credentials_ok,
    )
    test_update = UpdateModelViewTest(
        payloads=collection_payloads,
        instance_getter=get_instance,
        credentials_getter=get_credentials_ok_forbidden,
    )
    test_delete = DeleteModelViewTest(
        instance_getter=get_instance, credentials_getter=get_credentials_ok_forbidden
    )

    item_payloads = Payloads(
        ok={"name": "new-name", "description": "new-description"},
    )

    test_list_items = ListModelViewTest(
        instance_getter=get_instance,
        credentials_getter=get_credentials_ok_forbidden,
    )
    test_create_item = CreateModelViewTest(
        payloads=item_payloads,
        instance_getter=get_instance,
        credentials_getter=get_credentials_ok_forbidden,
    )
