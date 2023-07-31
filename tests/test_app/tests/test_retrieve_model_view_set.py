from unittest.mock import MagicMock

from django.db import models
from django.test import TestCase

from ninja_crud.views import RetrieveModelView
from tests.test_app.models import Item
from tests.test_app.schemas import ItemOut


class TestRetrieveModelViewSet(TestCase):
    def test_register_route_router_kwargs(self):
        router_mock = MagicMock()
        model_view = RetrieveModelView(
            output_schema=ItemOut,
            router_kwargs={"exclude_unset": True},
        )

        model_view.register_route(router_mock, Item)

        router_mock.get.assert_called_once()
        self.assertTrue(router_mock.get.call_args[1]["exclude_unset"])
