from unittest.mock import MagicMock

from django.test import TestCase

from ninja_crud.views import DeleteModelView
from tests.test_app.models import Collection


class TestDeleteModelView(TestCase):
    def test_register_route_router_kwargs(self):
        router_mock = MagicMock()
        delete_collection = DeleteModelView(router_kwargs={"exclude_unset": True})

        delete_collection.register_route(router_mock, "delete_collection", Collection)

        router_mock.api_operation.assert_called_once()
        self.assertTrue(router_mock.api_operation.call_args[1]["exclude_unset"])
