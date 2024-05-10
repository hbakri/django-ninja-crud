import unittest
import uuid

import django.core.exceptions

from ninja_crud.views.helpers import PathParametersTypeResolver
from tests.test_app.models import Item


class TestPathParametersTypeResolver(unittest.TestCase):
    def test_resolve(self):
        path_parameters_type = PathParametersTypeResolver.resolve(
            path="/{id}", model_class=Item
        )
        self.assertIsNotNone(path_parameters_type)
        self.assertIsNotNone(path_parameters_type.__fields__.get("id"))
        self.assertEqual(
            path_parameters_type.__fields__.get("id").annotation, uuid.UUID
        )

        path_parameters_type = PathParametersTypeResolver.resolve(
            path="/{collection_id}", model_class=Item
        )
        self.assertIsNotNone(path_parameters_type)
        self.assertIsNotNone(path_parameters_type.__fields__.get("collection_id"))
        self.assertEqual(
            path_parameters_type.__fields__.get("collection_id").annotation, uuid.UUID
        )

    def test_resolve_field_type(self):
        self.assertEqual(
            PathParametersTypeResolver._resolve_field_type(
                model_class=Item, field_name="id"
            ),
            uuid.UUID,
        )
        self.assertEqual(
            PathParametersTypeResolver._resolve_field_type(
                model_class=Item, field_name="name"
            ),
            str,
        )
        self.assertEqual(
            PathParametersTypeResolver._resolve_field_type(
                model_class=Item, field_name="description"
            ),
            str,
        )
        self.assertEqual(
            PathParametersTypeResolver._resolve_field_type(
                model_class=Item, field_name="collection_id"
            ),
            uuid.UUID,
        )

        with self.assertRaises(ValueError):
            PathParametersTypeResolver._resolve_field_type(
                model_class=Item, field_name="collection"
            )

        with self.assertRaises(django.core.exceptions.FieldDoesNotExist):
            PathParametersTypeResolver._resolve_field_type(
                model_class=Item, field_name="non_existing_field"
            )
