from unittest.mock import MagicMock

from django.test import TestCase

from ninja_crud import views, viewsets
from tests.test_app.models import Collection, Item
from tests.test_app.schemas import ItemIn, ItemOut


class TestCreateModelView(TestCase):
    def test_register_route_with_router_kwargs(self):
        router_mock = MagicMock()

        class ItemViewSet(viewsets.ModelViewSet):
            model = Item

            create_item = views.CreateModelView(
                request_body=ItemIn,
                response_body=ItemOut,
                router_kwargs={"exclude_unset": True},
            )

        ItemViewSet.create_item.register_route(router_mock, "create_item")

        router_mock.api_operation.assert_called_once()
        self.assertTrue(router_mock.api_operation.call_args[1]["exclude_unset"])

    # noinspection PyTypeChecker
    def test_model_factory_validator(self):
        # model_factory must be callable
        with self.assertRaises(TypeError):
            views.CreateModelView(
                path="/{id}/items/",
                model_factory="not callable",
                request_body=ItemIn,
                response_body=ItemOut,
            )

        # model_factory must have the correct number of arguments
        with self.assertRaises(ValueError):
            views.CreateModelView(
                path="/{id}/items/",
                model_factory=lambda: Item(),
                request_body=ItemIn,
                response_body=ItemOut,
            )

        with self.assertRaises(ValueError):
            views.CreateModelView(
                model_factory=lambda id: Collection(),
                request_body=ItemIn,
                response_body=ItemOut,
            )
