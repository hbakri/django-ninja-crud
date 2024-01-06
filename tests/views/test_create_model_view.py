from unittest.mock import MagicMock

from django.test import TestCase

from ninja_crud.views.create_model_view import CreateModelView
from tests.test_app.models import Collection, Item
from tests.test_app.schemas import ItemIn, ItemOut


class TestCreateModelView(TestCase):
    def test_register_route_with_router_kwargs(self):
        router_mock = MagicMock()
        create_item = CreateModelView(
            payload_schema=ItemIn,
            response_schema=ItemOut,
            router_kwargs={"exclude_unset": True},
        )

        create_item.register_route(router_mock, "create_item", Item)

        router_mock.api_operation.assert_called_once()
        self.assertTrue(router_mock.api_operation.call_args[1]["exclude_unset"])

    # noinspection PyTypeChecker
    def test_model_factory_validator(self):
        # model_factory must be callable
        with self.assertRaises(TypeError):
            CreateModelView(
                path="/{id}/items/",
                model_factory="not callable",
                payload_schema=ItemIn,
                response_schema=ItemOut,
            )

        # model_factory must have the correct number of arguments
        with self.assertRaises(ValueError):
            CreateModelView(
                path="/{id}/items/",
                model_factory=lambda: Item(),
                payload_schema=ItemIn,
                response_schema=ItemOut,
            )

        with self.assertRaises(ValueError):
            CreateModelView(
                model_factory=lambda id: Collection(),
                payload_schema=ItemIn,
                response_schema=ItemOut,
            )
