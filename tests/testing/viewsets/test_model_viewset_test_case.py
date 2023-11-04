import unittest
from unittest.mock import patch

from examples.models import Department
from examples.schemas import DepartmentOut
from ninja_crud.testing.views import ListModelViewTest
from ninja_crud.testing.viewsets import ModelViewSetTestCase
from ninja_crud.views import ListModelView
from ninja_crud.viewsets import ModelViewSet


class TestModelViewSetTestCase(unittest.TestCase):
    def test_get_associated_model_view_ok(self):
        class ExampleModelViewSet(ModelViewSet):
            model = Department

            list_view = ListModelView(output_schema=DepartmentOut)

        class TestExampleModelViewSet(ModelViewSetTestCase):
            test_list_view = ListModelViewTest()

        TestExampleModelViewSet.model_viewset_class = ExampleModelViewSet
        associated_model_view = TestExampleModelViewSet._get_associated_model_view(
            test_attr_name="test_list_view", model_view_class=ListModelView
        )
        self.assertEqual(associated_model_view, ExampleModelViewSet.list_view)

    def test_get_associated_model_view_not_found(self):
        class ExampleModelViewSet(ModelViewSet):
            model = Department

        class TestExampleModelViewSet(ModelViewSetTestCase):
            test_list_view = ListModelViewTest()

        TestExampleModelViewSet.model_viewset_class = ExampleModelViewSet
        with self.assertRaises(ValueError):
            TestExampleModelViewSet._get_associated_model_view(
                test_attr_name="test_list_view", model_view_class=ListModelView
            )

    def test_check_all_model_views_associated_ok(self):
        class ExampleModelViewSet(ModelViewSet):
            model = Department

            list_view = ListModelView(output_schema=DepartmentOut)

        class TestExampleModelViewSet(ModelViewSetTestCase):
            test_list_view = ListModelViewTest()

        TestExampleModelViewSet.model_viewset_class = ExampleModelViewSet
        TestExampleModelViewSet._check_all_model_views_associated(
            associated_model_views=[ExampleModelViewSet.list_view]
        )

    def test_check_all_model_views_associated_not_found(self):
        class ExampleModelViewSet(ModelViewSet):
            model = Department

            list_view = ListModelView(output_schema=DepartmentOut)
            other_list_view = ListModelView(output_schema=DepartmentOut)

        class TestExampleModelViewSet(ModelViewSetTestCase):
            test_list_view = ListModelViewTest()

        TestExampleModelViewSet.model_viewset_class = ExampleModelViewSet
        with patch(
            "ninja_crud.testing.viewsets.model_viewset_test_case.logger"
        ) as mock_logger:
            TestExampleModelViewSet._check_all_model_views_associated(
                associated_model_views=[ExampleModelViewSet.list_view]
            )
            mock_logger.warning.assert_called_once()

    def test_validate_base_path_wrong_type(self):
        class TestExampleModelViewSet(ModelViewSetTestCase):
            base_path = 0

        with self.assertRaises(TypeError):
            TestExampleModelViewSet._validate_base_path()
