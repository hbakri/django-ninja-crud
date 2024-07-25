import unittest
import uuid
from typing import Optional

import django.core.exceptions
import ninja
from packaging import version

from ninja_crud.views.helpers import PathParametersTypeResolver
from tests.test_app.models import Item


class TestPathParametersTypeResolver(unittest.TestCase):
    def test_resolve(self):
        path_parameters_type = PathParametersTypeResolver.resolve(
            path="/{id}", model_class=Item
        )
        ninja_v1_2_0 = version.parse(ninja.__version__) >= version.parse("1.2.0")
        expected_id_type = Optional[uuid.UUID] if ninja_v1_2_0 else uuid.UUID

        self.assertEqual(
            path_parameters_type.model_fields.get("id").annotation, expected_id_type
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
            path_parameters_type.model_fields.get("id").annotation, expected_id_type
        )

        with self.assertRaises(django.core.exceptions.FieldDoesNotExist):
            PathParametersTypeResolver.resolve(
                path="/{nonexistent_field}", model_class=Item
            )
