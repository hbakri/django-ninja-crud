from unittest.mock import MagicMock

from django.test import TestCase

from ninja_crud import views, viewsets
from ninja_crud.views.enums import HTTPMethod
from tests.test_app.models import Item
from tests.test_app.schemas import ItemIn, ItemOut


class TestUpdateModelView(TestCase):
    def test_register_route_router_kwargs(self):
        router_mock = MagicMock()

        class ItemViewSet(viewsets.ModelViewSet):
            model = Item

            update_item = views.UpdateModelView(
                payload_schema=ItemIn,
                response_schema=ItemOut,
                router_kwargs={"exclude_unset": True},
            )

        ItemViewSet.update_item.register_route(router_mock, "update_item")

        router_mock.api_operation.assert_called_once()
        self.assertTrue(router_mock.api_operation.call_args[1]["exclude_unset"])

    def test_method_validator(self):
        with self.assertRaises(TypeError):
            # noinspection PyTypeChecker
            views.UpdateModelView(
                method=1,
                payload_schema=ItemIn,
                response_schema=ItemOut,
            )

        with self.assertRaises(ValueError):
            views.UpdateModelView(
                payload_schema=ItemIn,
                response_schema=ItemOut,
                method=HTTPMethod.GET,
            )
