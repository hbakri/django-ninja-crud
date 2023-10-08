import unittest

from ninja_crud.views.validators.path_validator import PathValidator


class TestPathValidator(unittest.TestCase):
    def test_validate_ok(self):
        PathValidator.validate(path="/", detail=False)
        PathValidator.validate(path="/{id}", detail=True)

    def test_validate_error(self):
        # path must be a string
        with self.assertRaises(TypeError):
            # noinspection PyTypeChecker
            PathValidator.validate(path=1, detail=False)

        # path must start with a slash
        with self.assertRaises(ValueError):
            PathValidator.validate(path="{id}", detail=True)

        # path for collection views must not have a path parameter
        with self.assertRaises(ValueError):
            PathValidator.validate(path="/{id}", detail=False)

        # path for detail views must have a path parameter
        with self.assertRaises(ValueError):
            PathValidator.validate(path="/", detail=True)
