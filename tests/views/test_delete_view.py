import uuid

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from django.test import TestCase
from pydantic import BaseModel

from ninja_crud import views, viewsets
from tests.test_app.models import Collection, Item
from tests.test_app.schemas import ItemIn, ItemOut


class TestDeleteView(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="user-1", password="password", email="email@example.com"
        )
        self.collection = Collection.objects.create(
            name="collection", created_by=self.user
        )
        self.item = Item.objects.create(name="item", collection=self.collection)
        self.delete_view = views.DeleteView(
            model=Item,
        )

        class PathParameters(BaseModel):
            id: uuid.UUID

        self.PathParameters = PathParameters

    def test_default_get_model_without_model(self):
        delete_view = views.DeleteView()
        with self.assertRaises(ValueError):
            delete_view.as_operation()

    def test_default_get_model(self):
        path_parameters = self.PathParameters(id=self.item.id)
        model_instance = self.delete_view._default_get_model(
            HttpRequest(), path_parameters
        )

        self.assertIsInstance(model_instance, Item)
        self.assertEqual(model_instance.id, self.item.id)

    def test_default_view_function(self):
        path_parameters = self.PathParameters(id=self.item.id)
        self.delete_view.handler(HttpRequest(), path_parameters)

        with self.assertRaises(ObjectDoesNotExist):
            Item.objects.get(id=self.item.id)

    def test_set_api_viewset_class(self):
        delete_view = views.DeleteView()

        class ItemViewSet(viewsets.APIViewSet):
            model = Item
            default_request_body = ItemIn
            default_response_body = ItemOut

        delete_view.api_viewset_class = ItemViewSet
        delete_view.as_operation()
        self.assertEqual(delete_view.model, Item)
        self.assertEqual(delete_view.response_body, None)
