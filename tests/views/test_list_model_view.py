from typing import List
from unittest.mock import MagicMock

from django.test import TestCase

from ninja_crud import views, viewsets
from tests.test_app.models import Item
from tests.test_app.schemas import ItemOut


class TestListModelView(TestCase):
    def test_register_route_with_router_kwargs(self):
        router_mock = MagicMock()

        class ItemViewSet(viewsets.ModelViewSet):
            model = Item

            list_items = views.ListModelView(
                response_body=List[ItemOut],
                router_kwargs={"exclude_unset": True},
            )

        ItemViewSet.list_items.register_route(router_mock, "list_items")

        router_mock.api_operation.assert_called_once()
        self.assertTrue(router_mock.api_operation.call_args[1]["exclude_unset"])

    def test_bind_to_viewset_without_response_body_error(self):
        model_view = views.ListModelView()

        class ItemModelViewSet(viewsets.ModelViewSet):
            model = Item

        with self.assertRaises(AttributeError):
            model_view.model_viewset_class = ItemModelViewSet
