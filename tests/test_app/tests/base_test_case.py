from django.contrib.auth.models import User
from django.test import TestCase

from tests.test_app.models import Collection, Item


class BaseTestCase(TestCase):
    user_1: User
    user_2: User
    collection_1: Collection
    collection_2: Collection
    item_1: Item
    item_2: Item

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user_1 = User.objects.create(
            username="user-1", password="password", email="email1@example.com"
        )
        cls.user_2 = User.objects.create(
            username="user-2", password="password", email="email2@example.com"
        )
        cls.collection_1 = Collection.objects.create(
            name="collection-1", created_by=cls.user_1
        )
        cls.collection_2 = Collection.objects.create(
            name="collection-2", created_by=cls.user_2
        )
        cls.item_1 = Item.objects.create(name="item-1", collection=cls.collection_1)
        cls.item_2 = Item.objects.create(name="item-2", collection=cls.collection_2)
