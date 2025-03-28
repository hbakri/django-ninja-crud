import uuid
from typing import Any
from unittest import mock

import django.core.exceptions
import ninja.constants
import pydantic
from django.test import TestCase

from ninja_crud import views, viewsets
from tests.test_app.models import Item


class TestAPIView(TestCase):
    def setUp(self):
        class ReusableAPIView(views.APIView):
            model = None

            def handler(self, *args: Any, **kwargs: Any) -> Any:
                """This is a handler method."""

            def as_operation(self) -> dict[str, Any]:
                if self.api_viewset_class and not self.model:
                    self.model = self.api_viewset_class.model
                return super().as_operation()

        self.api_view = ReusableAPIView(
            name="delete_item",
            methods=["DELETE"],
            path="/{id}",
            status_code=204,
            response_schema=None,
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

        self.assertIsNone(self.api_view.api_viewset_class)
        self.api_view.api_viewset_class = ViewSet
        self.assertEqual(self.api_view.api_viewset_class, ViewSet)

        with self.assertRaises(ValueError):
            self.api_view.api_viewset_class = ViewSet

        self.api_view.as_operation()
        self.assertEqual(self.api_view.model, Item)
        self.assertIsNotNone(self.api_view.resolve_path_parameters(model=Item))

    def test_resolve_path_parameters(self):
        self.api_view.path = "/{id}"
        self.api_view.model = Item
        path_parameters_type = self.api_view.resolve_path_parameters(model=Item)
        self.assertEqual(
            path_parameters_type.model_fields.get("id").annotation, uuid.UUID
        )

        self.api_view.path = "/{collection_id}"
        path_parameters_type = self.api_view.resolve_path_parameters(model=Item)
        self.assertEqual(
            path_parameters_type.model_fields.get("collection_id").annotation, uuid.UUID
        )

        self.api_view.path = "/{collection_id}/items/{id}"
        path_parameters_type = self.api_view.resolve_path_parameters(model=Item)
        self.assertEqual(
            path_parameters_type.model_fields.get("collection_id").annotation, uuid.UUID
        )
        self.assertEqual(
            path_parameters_type.model_fields.get("id").annotation, uuid.UUID
        )

        with self.assertRaises(django.core.exceptions.FieldDoesNotExist):
            self.api_view.path = "/{nonexistent_field}"
            self.api_view.resolve_path_parameters(model=Item)

    def test_resolve_response(self):
        model_1 = pydantic.create_model("Model1", field_1=(str, ...))
        model_2 = pydantic.create_model("Model2", field_2=(int, ...))

        class CustomAPIView(views.APIView):
            def handler(self, *args: Any, **kwargs: Any) -> Any:
                """This is a handler method."""

        api_view = CustomAPIView(path="/{id}", methods=["GET"])
        self.assertEqual(api_view.as_operation()["response"], ninja.constants.NOT_SET)

        api_view = CustomAPIView(path="/{id}", methods=["GET"], response_schema=model_1)
        self.assertEqual(api_view.as_operation()["response"], {200: model_1})

        api_view = CustomAPIView(path="/{id}", methods=["DELETE"], status_code=204)
        self.assertEqual(api_view.as_operation()["response"], {204: None})

        api_view = CustomAPIView(
            path="/{id}", methods=["GET"], responses={200: model_1, 201: model_2}
        )
        self.assertEqual(
            api_view.as_operation()["response"], {200: model_1, 201: model_2}
        )

        api_view = CustomAPIView(
            path="/{id}", methods=["GET"], response_schema=model_1, status_code=200
        )
        self.assertEqual(api_view.as_operation()["response"], {200: model_1})

        api_view = CustomAPIView(
            path="/{id}", methods=["DELETE"], status_code=204, responses={404: str}
        )
        self.assertEqual(api_view.as_operation()["response"], {204: None, 404: str})

        api_view = CustomAPIView(
            path="/{id}", methods=["GET"], response_schema=model_1, responses={404: str}
        )
        self.assertEqual(api_view.as_operation()["response"], {200: model_1, 404: str})

        api_view = CustomAPIView(
            path="/{id}",
            methods=["GET"],
            response_schema=model_1,
            status_code=201,
            responses={404: str},
        )
        self.assertEqual(api_view.as_operation()["response"], {201: model_1, 404: str})
