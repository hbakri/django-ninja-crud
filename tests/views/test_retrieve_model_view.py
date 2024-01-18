from unittest.mock import MagicMock

from django.test import TestCase

from ninja_crud import views, viewsets
from ninja_crud.viewsets import ModelViewSet
from tests.test_app.models import Item
from tests.test_app.schemas import ItemOut


class TestRetrieveModelView(TestCase):
    def test_register_route_router_kwargs(self):
        router_mock = MagicMock()

        class ItemViewSet(viewsets.ModelViewSet):
            model = Item

            retrieve_item = views.RetrieveModelView(
                response_schema=ItemOut,
                router_kwargs={"exclude_unset": True},
            )

        ItemViewSet.retrieve_item.register_route(router_mock, "retrieve_item")

        router_mock.api_operation.assert_called_once()
        self.assertTrue(router_mock.api_operation.call_args[1]["exclude_unset"])

    # noinspection PyTypeChecker
    def test_queryset_getter_validator(self):
        # queryset_getter must be callable
        with self.assertRaises(TypeError):
            views.RetrieveModelView(
                queryset_getter="not callable",
                response_schema=ItemOut,
            )

        # queryset_getter must have the correct number of arguments
        with self.assertRaises(ValueError):
            views.RetrieveModelView(
                queryset_getter=lambda: Item.objects.get_queryset(),
                response_schema=ItemOut,
            )

    def test_bind_to_viewset_with_response_schema(self):
        model_view = views.RetrieveModelView(response_schema=ItemOut)

        class ItemModelViewSet(ModelViewSet):
            model = Item
            default_request_body = None
            default_response_body = None

        model_view.model_viewset_class = ItemModelViewSet

    def test_bind_to_viewset_without_response_schema(self):
        model_view = views.RetrieveModelView()

        class ItemModelViewSet(ModelViewSet):
            model = Item
            default_request_body = None
            default_response_body = ItemOut

        model_view.model_viewset_class = ItemModelViewSet

    def test_bind_to_viewset_without_response_schema_error(self):
        model_view = views.RetrieveModelView()

        class ItemModelViewSet(ModelViewSet):
            model = Item

        with self.assertRaises(AttributeError):
            model_view.model_viewset_class = ItemModelViewSet
