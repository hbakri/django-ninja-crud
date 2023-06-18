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
from tests.test_app.models import Collection, Item
from tests.test_app.views.view_collection import CollectionViewSet


class CollectionViewSetTest(ModelViewSetTest, TestCase):
    model_view_set = CollectionViewSet
    collection_1: Collection
    collection_2: Collection
    item: Item

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.collection_1 = Collection.objects.create(name="collection-1")
        cls.collection_2 = Collection.objects.create(name="collection-2")
        cls.item = Item.objects.create(name="item-1", collection=cls.collection_1)
        cls.token = "supersecret"

    def get_instance(self: Union["CollectionViewSetTest", TestCase]):
        return self.collection_1

    def get_credentials(self: Union["CollectionViewSetTest", TestCase]):
        return Credentials(
            ok={"HTTP_AUTHORIZATION": f"Bearer {self.token}"}, unauthorized={}
        )

    collection_payloads = Payloads(
        ok={"name": "new-name", "description": "new-description"},
        bad_request={"unknown_field": "unknown_field"},
        conflict={"name": "collection-2"},
    )

    test_list = ListModelViewTest(
        instance_getter=get_instance,
        credentials_getter=get_credentials,
    )
    test_create = CreateModelViewTest(
        payloads=collection_payloads,
        instance_getter=get_instance,
        credentials_getter=get_credentials,
    )
    test_retrieve = RetrieveModelViewTest(
        instance_getter=get_instance,
        credentials_getter=get_credentials,
    )
    test_update = UpdateModelViewTest(
        payloads=collection_payloads,
        instance_getter=get_instance,
        credentials_getter=get_credentials,
    )
    test_delete = DeleteModelViewTest(
        instance_getter=get_instance, credentials_getter=get_credentials
    )

    item_payloads = Payloads(
        ok={"name": "new-name", "description": "new-description"},
        bad_request={"unknown_field": 1},
    )

    test_list_items = ListModelViewTest(
        instance_getter=get_instance,
        credentials_getter=get_credentials,
    )
    test_create_item = CreateModelViewTest(
        payloads=item_payloads,
        instance_getter=get_instance,
        credentials_getter=get_credentials,
    )
