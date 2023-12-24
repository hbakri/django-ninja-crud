from unittest.mock import MagicMock

from django.test import TestCase

from ninja_crud.views.list_model_view import ListModelView
from tests.test_app.models import Item
from tests.test_app.schemas import ItemOut


class TestListModelView(TestCase):
    def test_register_route_with_router_kwargs(self):
        router_mock = MagicMock()
        list_items = ListModelView(
            output_schema=ItemOut,
            router_kwargs={"exclude_unset": True},
        )

        list_items.register_route(router_mock, "list_items", Item)

        router_mock.api_operation.assert_called_once()
        self.assertTrue(router_mock.api_operation.call_args[1]["exclude_unset"])

    # noinspection PyTypeChecker
    def test_queryset_getter_validator(self):
        # queryset_getter must be provided if detail=True
        with self.assertRaises(ValueError):
            ListModelView(
                detail=True,
                queryset_getter=None,
                output_schema=ItemOut,
            )

        # queryset_getter must be callable
        with self.assertRaises(TypeError):
            ListModelView(
                detail=True,
                queryset_getter="not callable",
                output_schema=ItemOut,
            )

        # queryset_getter must return a queryset
        with self.assertRaises(TypeError):
            ListModelView(
                detail=True,
                queryset_getter=lambda id: None,
                output_schema=ItemOut,
            )

        # queryset_getter must have the correct number of arguments
        with self.assertRaises(ValueError):
            ListModelView(
                detail=True,
                queryset_getter=lambda: Item.objects.get_queryset(),
                output_schema=ItemOut,
            )

        with self.assertRaises(ValueError):
            ListModelView(
                detail=False,
                queryset_getter=lambda id: Item.objects.get_queryset(),
                output_schema=ItemOut,
            )
