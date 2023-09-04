import uuid

from django.test import TestCase
from example.models import Department, Employee
from example.views.view_department import DepartmentViewSet

from ninja_crud.tests import (
    CreateModelViewTest,
    PathParameters,
    Payloads,
    TestDeleteModelView,
    TestListModelView,
    TestModelViewSet,
    TestRetrieveModelView,
    TestUpdateModelView,
)


class TestDepartmentViewSet(TestModelViewSet, TestCase):
    model_view_set_class = DepartmentViewSet
    base_path = "api/departments"

    department_1: Department
    department_2: Department
    employee: Employee

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.department_1 = Department.objects.create(title="department-1")
        cls.department_2 = Department.objects.create(title="department-2")
        cls.employee = Employee.objects.create(
            first_name="first_name", last_name="last_name", department=cls.department_1
        )
        cls.token = "supersecret"

    def get_path_parameters(self):
        return PathParameters(
            ok={"id": self.department_1.id}, not_found={"id": uuid.uuid4()}
        )

    department_payloads = Payloads(
        ok={"title": "new_title"},
        bad_request={"bad-title": 1},
        conflict={"title": "department-2"},
    )

    test_list = TestListModelView()
    test_create = CreateModelViewTest(payloads=department_payloads)
    test_retrieve = TestRetrieveModelView(path_parameters=get_path_parameters)
    test_update = TestUpdateModelView(
        path_parameters=get_path_parameters, payloads=department_payloads
    )
    test_delete = TestDeleteModelView(path_parameters=get_path_parameters)

    employee_payloads = Payloads(
        ok={
            "first_name": "new_first_name",
            "last_name": "new_last_name",
        },
        bad_request={"first_name": 1},
    )

    test_list_employees = TestListModelView(path_parameters=get_path_parameters)
    test_create_employee = CreateModelViewTest(
        path_parameters=get_path_parameters, payloads=employee_payloads
    )
