import unittest

from examples.schemas import DepartmentIn, DepartmentOut
from ninja_crud.viewsets import ModelViewSet


class TestModelViewSet(unittest.TestCase):
    def test_validate_default_schemas(self):
        class DepartmentModelViewSet(ModelViewSet):
            default_input_schema = DepartmentIn
            default_output_schema = DepartmentOut

        DepartmentModelViewSet._validate_input_schema_class(optional=False)
        DepartmentModelViewSet._validate_output_schema_class(optional=False)

    def test_validate_default_schemas_optional(self):
        class DepartmentModelViewSet(ModelViewSet):
            default_input_schema = None
            default_output_schema = None

        DepartmentModelViewSet._validate_input_schema_class(optional=True)
        DepartmentModelViewSet._validate_output_schema_class(optional=True)

    def test_validate_default_schemas_missing(self):
        class DepartmentModelViewSet(ModelViewSet):
            pass

        with self.assertRaises(ValueError):
            DepartmentModelViewSet._validate_input_schema_class(optional=False)

        with self.assertRaises(ValueError):
            DepartmentModelViewSet._validate_output_schema_class(optional=False)

    def test_validate_default_schemas_wrong_type(self):
        class DepartmentModelViewSet(ModelViewSet):
            default_input_schema = 0
            default_output_schema = 0

        with self.assertRaises(TypeError):
            DepartmentModelViewSet._validate_input_schema_class(optional=False)

        with self.assertRaises(TypeError):
            DepartmentModelViewSet._validate_output_schema_class(optional=False)
