from typing import List

from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.http import HttpRequest
from django.test import TestCase
from ninja import FilterSchema, Schema

from ninja_crud import views, viewsets
from tests.test_app.models import Collection, Item
from tests.test_app.schemas import ItemFilter, ItemIn, ItemOut


class TestListView(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="user-1", password="password", email="email@example.com"
        )
        self.collection = Collection.objects.create(
            name="collection", created_by=self.user
        )
        self.item1 = Item.objects.create(name="item1", collection=self.collection)
        self.item2 = Item.objects.create(name="item2", collection=self.collection)
        self.list_view = views.ListView(
            response_body=List[ItemOut],
            model=Item,
        )

    def test_default_get_queryset_without_model(self):
        list_view = views.ListView()
        with self.assertRaises(ValueError):
            list_view.as_operation()

    def test_default_get_queryset(self):
        queryset = self.list_view._default_get_queryset(HttpRequest(), None)

        self.assertIsInstance(queryset, QuerySet)
        self.assertEqual(list(queryset), [self.item1, self.item2])

    def test_default_filter_queryset_with_schema(self):
        queryset = Item.objects.all()

        class QueryParameters(Schema):
            name: str

        query_parameters = QueryParameters(name="item1")
        filtered_queryset = self.list_view._default_filter_queryset(
            queryset, query_parameters
        )

        self.assertIsInstance(filtered_queryset, QuerySet)
        self.assertEqual(list(filtered_queryset), [self.item1])

    def test_default_filter_queryset_with_filter_schema(self):
        queryset = Item.objects.all()

        class QueryParameters(FilterSchema):
            name: str

        query_parameters = QueryParameters(name="item1")
        filtered_queryset = self.list_view._default_filter_queryset(
            queryset, query_parameters
        )

        self.assertIsInstance(filtered_queryset, QuerySet)
        self.assertEqual(list(filtered_queryset), [self.item1])

    def test_default_view_function(self):
        query_parameters = ItemFilter(name="item1")
        result = self.list_view.handler(HttpRequest(), None, query_parameters)

        self.assertIsInstance(result, QuerySet)
        self.assertEqual(list(result), [self.item1])

    def test_set_api_viewset_class(self):
        list_view = views.ListView()

        class ItemViewSet(viewsets.APIViewSet):
            model = Item
            default_request_body = ItemIn
            default_response_body = ItemOut

        list_view.api_viewset_class = ItemViewSet
        list_view.as_operation()
        self.assertEqual(list_view.model, Item)
        self.assertEqual(list_view.response_body, List[ItemOut])
