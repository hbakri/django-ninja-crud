import unittest

from ninja_crud.testing.core.components import utils


class TestUtils(unittest.TestCase):
    def test_ensure_list_of_dicts_single_dict(self):
        data = {"key": "value"}
        result = utils.ensure_list_of_dicts(data=data)
        self.assertEqual(result, [data])

    def test_ensure_list_of_dicts_list_of_dicts(self):
        data = [{"key": "value"}]
        result = utils.ensure_list_of_dicts(data=data)
        self.assertEqual(result, data)

    def test_ensure_list_of_dicts_empty_list(self):
        data = []
        with self.assertRaises(ValueError):
            utils.ensure_list_of_dicts(data=data)

    def test_ensure_list_of_dicts_not_list_or_dict(self):
        data = 1
        with self.assertRaises(TypeError):
            # noinspection PyTypeChecker
            utils.ensure_list_of_dicts(data=data)
