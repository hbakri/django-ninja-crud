from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from django.test import TestCase

from ninja_crud import views, viewsets
from tests.test_app.models import Collection
from tests.test_app.schemas import CollectionIn, CollectionOut


class TestCreateView(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="user-1", password="password", email="email@example.com"
        )
        self.create_view = views.CreateView(
            request_body=CollectionIn,
            response_body=CollectionOut,
            model=Collection,
        )

    def test_default_init_model_without_model(self):
        create_view = views.CreateView()
        with self.assertRaises(ValueError):
            create_view.as_operation()

    def test_default_init_model(self):
        model_instance = self.create_view.init_model(HttpRequest(), None)

        self.assertIsInstance(model_instance, Collection)
        with self.assertRaises(ObjectDoesNotExist):
            Collection.objects.get(id=model_instance.id)

    def test_default_view_function(self):
        self.create_view.pre_save = lambda request, instance: setattr(
            instance, "created_by", self.user
        )
        request_body = CollectionIn(name="new-collection")
        new_instance = self.create_view.handler(HttpRequest(), None, request_body)

        self.assertIsInstance(new_instance, Collection)
        self.assertIsNotNone(new_instance.id)
        self.assertEqual(new_instance.name, "new-collection")

    def test_set_api_viewset_class(self):
        create_view = views.CreateView()

        class CollectionViewSet(viewsets.APIViewSet):
            model = Collection
            default_request_body = CollectionIn
            default_response_body = CollectionOut

        create_view.api_viewset_class = CollectionViewSet
        create_view.as_operation()
        self.assertEqual(create_view.model, Collection)
        self.assertEqual(create_view.request_body, CollectionIn)
        self.assertEqual(create_view.response_schema, CollectionOut)
