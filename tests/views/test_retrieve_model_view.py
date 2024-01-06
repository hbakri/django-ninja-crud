from unittest.mock import MagicMock

from django.test import TestCase

from ninja_crud.views import RetrieveModelView
from ninja_crud.viewsets import ModelViewSet
from tests.test_app.models import Item
from tests.test_app.schemas import ItemOut


class TestRetrieveModelView(TestCase):
    def test_register_route_router_kwargs(self):
        router_mock = MagicMock()
        retrieve_item = RetrieveModelView(
            response_schema=ItemOut,
            router_kwargs={"exclude_unset": True},
        )

        retrieve_item.register_route(router_mock, "retrieve_item", Item)

        router_mock.api_operation.assert_called_once()
        self.assertTrue(router_mock.api_operation.call_args[1]["exclude_unset"])

    # noinspection PyTypeChecker
    def test_queryset_getter_validator(self):
        # queryset_getter must be callable
        with self.assertRaises(TypeError):
            RetrieveModelView(
                queryset_getter="not callable",
                response_schema=ItemOut,
            )

        # queryset_getter must have the correct number of arguments
        with self.assertRaises(ValueError):
            RetrieveModelView(
                queryset_getter=lambda: Item.objects.get_queryset(),
                response_schema=ItemOut,
            )

    def test_bind_to_viewset_with_response_schema(self):
        model_view = RetrieveModelView(response_schema=ItemOut)

        class ItemModelViewSet(ModelViewSet):
            model = Item
            default_payload_schema = None
            default_response_schema = None

        model_view.bind_to_viewset(ItemModelViewSet, model_view_name="retrieve")

    def test_bind_to_viewset_without_response_schema(self):
        model_view = RetrieveModelView()

        class ItemModelViewSet(ModelViewSet):
            model = Item
            default_payload_schema = None
            default_response_schema = ItemOut

        model_view.bind_to_viewset(ItemModelViewSet, model_view_name="retrieve")

    def test_bind_to_viewset_without_response_schema_error(self):
        model_view = RetrieveModelView()

        class ItemModelViewSet(ModelViewSet):
            model = Item
            default_payload_schema = None
            default_response_schema = None

        with self.assertRaises(ValueError):
            model_view.bind_to_viewset(ItemModelViewSet, model_view_name="retrieve")
