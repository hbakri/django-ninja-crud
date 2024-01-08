from unittest.mock import MagicMock

from django.test import TestCase

from ninja_crud import views, viewsets
from tests.test_app.models import Item


class TestDeleteModelView(TestCase):
    def test_register_route_router_kwargs(self):
        router_mock = MagicMock()

        class ItemViewSet(viewsets.ModelViewSet):
            model = Item

            delete_item = views.DeleteModelView(router_kwargs={"exclude_unset": True})

        ItemViewSet.delete_item.register_route(router_mock, "delete_item")

        router_mock.api_operation.assert_called_once()
        self.assertTrue(router_mock.api_operation.call_args[1]["exclude_unset"])
