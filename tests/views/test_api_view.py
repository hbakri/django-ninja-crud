from typing import Any
from unittest import mock

from django.test import TestCase

from ninja_crud import views, viewsets
from tests.test_app.models import Item


class TestAPIView(TestCase):
    def setUp(self):
        class ReusableAPIView(views.APIView):
            def handler(self, *args: Any, **kwargs: Any) -> Any:
                """
                This is a handler method.
                """

        self.api_view = ReusableAPIView(
            name="delete_item",
            method="DELETE",
            path="/{id}",
            response_status=204,
            response_body=None,
        )

    def test_as_operation(self):
        expected_operation = {
            "path": "/{id}",
            "methods": ["DELETE"],
            "view_func": mock.ANY,
            "response": {204: None},
        }
        actual_operation = self.api_view.as_operation()

        self.assertEqual(expected_operation, actual_operation)

    def test_view_func(self):
        def decorator_1(func: Any) -> Any:
            func.__name__ = f"decorator_1_{func.__name__}"
            return func

        def decorator_2(func: Any) -> Any:
            func.__name__ = f"decorator_2_{func.__name__}"
            return func

        self.api_view.decorators = [decorator_1, decorator_2] + self.api_view.decorators

        view_func = self.api_view.as_operation()["view_func"]

        self.assertEqual(
            view_func.__name__,
            f"decorator_1_decorator_2_{self.api_view.name}",
        )
        self.assertEqual(
            view_func.__annotations__,
            {
                "args": Any,
                "kwargs": Any,
                "return": Any,
            },
        )

    def test_api_viewset_class(self):
        class ViewSet(viewsets.APIViewSet):
            model = Item

        with self.assertRaises(ValueError):
            _ = self.api_view.get_api_viewset_class()

        self.api_view.set_api_viewset_class(ViewSet)
        self.assertEqual(self.api_view.get_api_viewset_class(), ViewSet)

        with self.assertRaises(ValueError):
            self.api_view.set_api_viewset_class(ViewSet)

        self.assertEqual(self.api_view.model, Item)
        self.assertIsNotNone(self.api_view.resolve_path_parameters())
