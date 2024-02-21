import http
import uuid
from typing import Any, Optional, Tuple, Union

import django.core.exceptions
import django.http
import django.test
import ninja

from ninja_crud import views
from tests.test_app.models import Item


class TestAbstractModelView(django.test.TestCase):
    def test_property_model_viewset_class(self):
        class ModelView(views.AbstractModelView):
            def handle_request(
                self,
                request: django.http.HttpRequest,
                path_parameters: Optional[ninja.Schema],
                query_parameters: Optional[ninja.Schema],
                request_body: Optional[ninja.Schema],
            ) -> Union[Any, Tuple[http.HTTPStatus, Any]]:
                pass

        class ItemViewSet:
            model = Item

        model_view = ModelView(method=views.enums.HTTPMethod.GET, path="/items/")

        self.assertIsNone(
            model_view.handle_request(
                request=django.http.HttpRequest(),
                path_parameters=None,
                query_parameters=None,
                request_body=None,
            )
        )

        with self.assertRaises(ValueError):
            _ = model_view.model_viewset_class

        model_view.model_viewset_class = ItemViewSet  # type: ignore

        with self.assertRaises(ValueError):
            model_view.model_viewset_class = ItemViewSet  # type: ignore

    def test_infer_field_type(self):
        self.assertEqual(
            views.AbstractModelView._infer_field_type(
                model_class=Item, field_name="id"
            ),
            uuid.UUID,
        )
        self.assertEqual(
            views.AbstractModelView._infer_field_type(
                model_class=Item, field_name="name"
            ),
            str,
        )
        self.assertEqual(
            views.AbstractModelView._infer_field_type(
                model_class=Item, field_name="description"
            ),
            str,
        )
        self.assertEqual(
            views.AbstractModelView._infer_field_type(
                model_class=Item, field_name="collection_id"
            ),
            uuid.UUID,
        )

        with self.assertRaises(ValueError):
            views.AbstractModelView._infer_field_type(
                model_class=Item, field_name="collection"
            )

        with self.assertRaises(django.core.exceptions.FieldDoesNotExist):
            views.AbstractModelView._infer_field_type(
                model_class=Item, field_name="non-existing-field"
            )
