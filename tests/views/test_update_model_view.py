from unittest.mock import MagicMock

from django.test import TestCase

from ninja_crud.views import UpdateModelView
from ninja_crud.views.enums import HTTPMethod
from tests.test_app.models import Item
from tests.test_app.schemas import ItemIn, ItemOut


class TestUpdateModelView(TestCase):
    def test_register_route_router_kwargs(self):
        router_mock = MagicMock()
        update_item = UpdateModelView(
            input_schema=ItemIn,
            output_schema=ItemOut,
            router_kwargs={"exclude_unset": True},
        )

        update_item.register_route(router_mock, "update_item", Item)

        router_mock.api_operation.assert_called_once()
        self.assertTrue(router_mock.api_operation.call_args[1]["exclude_unset"])

    def test_method_validator(self):
        with self.assertRaises(ValueError):
            UpdateModelView(
                input_schema=ItemIn,
                output_schema=ItemOut,
                method=HTTPMethod.GET,
            )

        with self.assertRaises(TypeError):
            # noinspection PyTypeChecker
            UpdateModelView(
                method=1,
                input_schema=ItemIn,
                output_schema=ItemOut,
            )
