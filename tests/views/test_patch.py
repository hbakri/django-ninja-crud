from unittest.mock import MagicMock

from django.db import models
from django.test import TestCase

from ninja_crud.views import PatchModelView
from tests.test_app.models import Item
from tests.test_app.schemas import ItemIn, ItemOut


class PatchModelViewTest(TestCase):
    def test_register_route_router_kwargs(self):
        router_mock = MagicMock()
        model_view = PatchModelView(
            input_schema=ItemIn,
            output_schema=ItemOut,
            router_kwargs={"exclude_unset": True},
        )

        model_view.register_route(router_mock, Item)

        router_mock.api_operation.assert_called_once()
        self.assertTrue(router_mock.api_operation.call_args[1]["exclude_unset"])
