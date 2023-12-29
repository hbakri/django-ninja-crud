import unittest

from ninja_crud.views.validators.path_validator import PathValidator


class TestPathValidator(unittest.TestCase):
    def test_validate_ok(self):
        PathValidator.validate(path="/", allow_no_parameters=True)
        PathValidator.validate(path="/{id}", allow_no_parameters=True)
        PathValidator.validate(path="{id}", allow_no_parameters=False)

    def test_validate_error(self):
        # path must be a string
        with self.assertRaises(TypeError):
            # noinspection PyTypeChecker
            PathValidator.validate(path=1, allow_no_parameters=True)

        # path for detail views must have exactly one id path parameter
        with self.assertRaises(ValueError):
            PathValidator.validate(path="/{name}", allow_no_parameters=False)

        # path for detail views must have a path parameter
        with self.assertRaises(ValueError):
            PathValidator.validate(path="/", allow_no_parameters=False)
