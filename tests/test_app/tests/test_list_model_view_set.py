from unittest.mock import MagicMock

from django.db import models
from django.test import TestCase

from ninja_crud.views.list import ListModelView
from tests.test_app.models import Collection, Item
from tests.test_app.schemas import ItemOut


class TestListModelViewSet(TestCase):
    def test_register_collection_route_router_kwargs(self):
        router_mock = MagicMock()
        model_view = ListModelView(
            output_schema=ItemOut,
            router_kwargs={"exclude_unset": True},
        )

        model_view.register_collection_route(router_mock, Item)

        router_mock.get.assert_called_once()
        self.assertTrue(router_mock.get.call_args[1]["exclude_unset"])

    def test_register_instance_route_router_kwargs(self):
        router_mock = MagicMock()
        model_view = ListModelView(
            output_schema=ItemOut,
            related_model=Collection,
            router_kwargs={"exclude_none": True},
        )

        model_view.register_instance_route(router_mock, Item)

        router_mock.get.assert_called_once()
        self.assertTrue(router_mock.get.call_args[1]["exclude_none"])
