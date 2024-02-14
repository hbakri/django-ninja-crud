from unittest.mock import MagicMock

from django.test import TestCase

from ninja_crud import views, viewsets
from tests.test_app.models import Item
from tests.test_app.schemas import ItemIn, ItemOut


class TestUpdateModelView(TestCase):
    def test_register_route_router_kwargs(self):
        router_mock = MagicMock()

        class ItemViewSet(viewsets.ModelViewSet):
            model = Item

            update_item = views.UpdateModelView(
                request_body=ItemIn,
                response_body=ItemOut,
                router_kwargs={"exclude_unset": True},
            )

        ItemViewSet.update_item.register_route(router_mock, "update_item")

        router_mock.api_operation.assert_called_once()
        self.assertTrue(router_mock.api_operation.call_args[1]["exclude_unset"])
