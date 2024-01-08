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
                response_schema=ItemOut,
                router_kwargs={"exclude_unset": True},
            )

        ItemViewSet.list_items.register_route(router_mock, "list_items")

        router_mock.api_operation.assert_called_once()
        self.assertTrue(router_mock.api_operation.call_args[1]["exclude_unset"])

    # noinspection PyTypeChecker
    def test_queryset_getter_validator(self):
        # queryset_getter must be callable
        with self.assertRaises(TypeError):
            views.ListModelView(
                path="/{id}/items/",
                queryset_getter="not callable",
                response_schema=ItemOut,
            )

        # queryset_getter must have the correct number of arguments
        with self.assertRaises(ValueError):
            views.ListModelView(
                path="/{id}/items/",
                queryset_getter=lambda: Item.objects.get_queryset(),
                response_schema=ItemOut,
            )

        with self.assertRaises(ValueError):
            views.ListModelView(
                queryset_getter=lambda id: Item.objects.get_queryset(),
                response_schema=ItemOut,
            )
