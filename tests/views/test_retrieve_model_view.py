from unittest.mock import MagicMock

from django.test import TestCase

from ninja_crud import views, viewsets
from ninja_crud.viewsets import ModelViewSet
from tests.test_app.models import Item
from tests.test_app.schemas import ItemOut


class TestReadModelView(TestCase):
    def test_register_route_router_kwargs(self):
        router_mock = MagicMock()

        class ItemViewSet(viewsets.ModelViewSet):
            model = Item

            read_item = views.ReadModelView(
                response_body=ItemOut,
                router_kwargs={"exclude_unset": True},
            )

        ItemViewSet.read_item.register_route(router_mock, "read_item")

        router_mock.api_operation.assert_called_once()
        self.assertTrue(router_mock.api_operation.call_args[1]["exclude_unset"])

    def test_bind_to_viewset_with_response_body(self):
        model_view = views.ReadModelView(response_body=ItemOut)

        class ItemModelViewSet(ModelViewSet):
            model = Item
            default_request_body = None
            default_response_body = None

        model_view.model_viewset_class = ItemModelViewSet

    def test_bind_to_viewset_without_response_body(self):
        model_view = views.ReadModelView()

        class ItemModelViewSet(ModelViewSet):
            model = Item
            default_request_body = None
            default_response_body = ItemOut

        model_view.model_viewset_class = ItemModelViewSet

    def test_bind_to_viewset_without_response_body_error(self):
        model_view = views.ReadModelView()

        class ItemModelViewSet(ModelViewSet):
            model = Item

        with self.assertRaises(AttributeError):
            model_view.model_viewset_class = ItemModelViewSet
