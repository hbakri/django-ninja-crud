from unittest.mock import MagicMock

from django.test import TestCase

from ninja_crud.views.create import CreateModelView
from tests.test_app.models import Collection, Item
from tests.test_app.schemas import ItemIn, ItemOut


class TestCreateModelView(TestCase):
    def test_register_route_with_router_kwargs(self):
        router_mock = MagicMock()
        model_view = CreateModelView(
            input_schema=ItemIn,
            output_schema=ItemOut,
            router_kwargs={"exclude_unset": True},
        )

        model_view.register_route(router_mock, Collection)

        router_mock.api_operation.assert_called_once()
        self.assertTrue(router_mock.api_operation.call_args[1]["exclude_unset"])

    # noinspection PyTypeChecker
    def test_model_factory_validator(self):
        # model_factory must be provided if detail=True
        with self.assertRaises(ValueError):
            CreateModelView(
                detail=True,
                model_factory=None,
                input_schema=ItemIn,
                output_schema=ItemOut,
            )

        # model_factory must be callable
        with self.assertRaises(TypeError):
            CreateModelView(
                detail=True,
                model_factory="not callable",
                input_schema=ItemIn,
                output_schema=ItemOut,
            )

        # model_factory must return an instance
        with self.assertRaises(TypeError):
            CreateModelView(
                detail=True,
                model_factory=lambda id: None,
                input_schema=ItemIn,
                output_schema=ItemOut,
            )

        # model_factory must have the correct number of arguments
        with self.assertRaises(ValueError):
            CreateModelView(
                detail=True,
                model_factory=lambda: Item(),
                input_schema=ItemIn,
                output_schema=ItemOut,
            )

        with self.assertRaises(ValueError):
            CreateModelView(
                detail=False,
                model_factory=lambda id: Collection(),
                input_schema=ItemIn,
                output_schema=ItemOut,
            )
