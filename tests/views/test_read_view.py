import uuid

from django.contrib.auth.models import User
from django.http import HttpRequest
from django.test import TestCase
from pydantic import BaseModel

from ninja_crud import views, viewsets
from tests.test_app.models import Collection, Item
from tests.test_app.schemas import ItemIn, ItemOut


class TestReadView(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="user-1", password="password", email="email@example.com"
        )
        self.collection = Collection.objects.create(
            name="collection", created_by=self.user
        )
        self.item = Item.objects.create(name="item", collection=self.collection)
        self.read_view = views.ReadView(
            response_body=ItemOut,
            model=Item,
        )

        class PathParameters(BaseModel):
            id: uuid.UUID

        self.PathParameters = PathParameters

    def test_default_get_model_without_model(self):
        read_view = views.ReadView()
        with self.assertRaises(ValueError):
            read_view.default_get_model(HttpRequest(), None)

    def test_default_get_model(self):
        path_parameters = self.PathParameters(id=self.item.id)
        model_instance = self.read_view.default_get_model(
            HttpRequest(), path_parameters
        )

        self.assertIsInstance(model_instance, Item)
        self.assertEqual(model_instance.id, self.item.id)

    def test_default_view_function(self):
        path_parameters = self.PathParameters(id=self.item.id)
        model_instance = self.read_view.default_view_function(
            HttpRequest(), path_parameters, None, None
        )

        self.assertIsInstance(model_instance, Item)
        self.assertEqual(model_instance.id, self.item.id)

    def test_set_api_viewset_class(self):
        read_view = views.ReadView()

        class ItemViewSet(viewsets.APIViewSet):
            model = Item
            default_request_body = ItemIn
            default_response_body = ItemOut

        read_view.set_api_viewset_class(ItemViewSet)
        self.assertEqual(read_view.model, Item)
        self.assertEqual(read_view.request_body, None)
        self.assertEqual(read_view.response_body, ItemOut)
