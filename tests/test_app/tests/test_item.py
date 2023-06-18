from typing import Union

from django.test import TestCase

from ninja_crud.tests import (
    Credentials,
    DeleteModelViewTest,
    ModelViewSetTest,
    Payloads,
    RetrieveModelViewTest,
    UpdateModelViewTest,
)
from tests.test_app.models import Collection, Item
from tests.test_app.views.view_item import ItemViewSet


class ItemViewSetTest(ModelViewSetTest, TestCase):
    model_view_set = ItemViewSet
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

    def get_instance(self: Union["ItemViewSetTest", TestCase]):
        return self.item

    def get_credentials(self: Union["ItemViewSetTest", TestCase]):
        return Credentials(
            ok={"HTTP_AUTHORIZATION": f"Bearer {self.token}"}, unauthorized={}
        )

    item_payloads = Payloads(
        ok={"name": "new-name", "description": "new-description"},
        bad_request={"unknown_field": 1},
    )

    test_retrieve = RetrieveModelViewTest(
        instance_getter=get_instance,
        credentials_getter=get_credentials,
    )
    test_update = UpdateModelViewTest(
        payloads=item_payloads,
        instance_getter=get_instance,
        credentials_getter=get_credentials,
    )
    test_delete = DeleteModelViewTest(
        instance_getter=get_instance, credentials_getter=get_credentials
    )
