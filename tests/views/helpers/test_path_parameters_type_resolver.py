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
        self.assertEqual(
            path_parameters_type.model_fields.get("id").annotation, uuid.UUID
        )

        path_parameters_type = PathParametersTypeResolver.resolve(
            path="/{collection_id}", model_class=Item
        )
        self.assertEqual(
            path_parameters_type.model_fields.get("collection_id").annotation, uuid.UUID
        )

        path_parameters_type = PathParametersTypeResolver.resolve(
            path="/{collection_id}/items/{id}", model_class=Item
        )
        self.assertEqual(
            path_parameters_type.model_fields.get("collection_id").annotation, uuid.UUID
        )
        self.assertEqual(
            path_parameters_type.model_fields.get("id").annotation, uuid.UUID
        )

        with self.assertRaises(django.core.exceptions.FieldDoesNotExist):
            PathParametersTypeResolver.resolve(
                path="/{nonexistent_field}", model_class=Item
            )
