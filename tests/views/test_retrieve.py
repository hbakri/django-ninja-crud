from unittest.mock import MagicMock

from django.test import TestCase

from ninja_crud.views import RetrieveModelView
from tests.test_app.models import Item
from tests.test_app.schemas import ItemOut


class TestRetrieveModelView(TestCase):
    def test_register_route_router_kwargs(self):
        router_mock = MagicMock()
        model_view = RetrieveModelView(
            output_schema=ItemOut,
            router_kwargs={"exclude_unset": True},
        )

        model_view.register_route(router_mock, Item)

        router_mock.get.assert_called_once()
        self.assertTrue(router_mock.get.call_args[1]["exclude_unset"])

    # noinspection PyTypeChecker
    def test_queryset_getter_validator(self):
        # queryset_getter must be callable
        with self.assertRaises(TypeError):
            RetrieveModelView(
                queryset_getter="not callable",
                output_schema=ItemOut,
            )

        # queryset_getter must return a queryset
        with self.assertRaises(TypeError):
            RetrieveModelView(
                queryset_getter=lambda id: None,
                output_schema=ItemOut,
            )

        # queryset_getter must have the correct number of arguments
        with self.assertRaises(ValueError):
            RetrieveModelView(
                queryset_getter=lambda: Item.objects.get_queryset(),
                output_schema=ItemOut,
            )
