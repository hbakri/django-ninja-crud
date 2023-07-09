import uuid

from django.test import TestCase
from example.models import Department, Employee
from example.views.view_employee import EmployeeViewSet

from ninja_crud.tests import (
    BodyParams,
    DeleteModelViewTest,
    ModelViewSetTest,
    PathParams,
    RetrieveModelViewTest,
    UpdateModelViewTest,
)


class EmployeeViewSetTest(ModelViewSetTest, TestCase):
    model_view_set = EmployeeViewSet
    urls_prefix = "api/employees"

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

    def get_path_params(self):
        return PathParams(ok={"id": self.employee.id}, not_found={"id": uuid.uuid4()})

    employee_body_params = BodyParams(
        ok={
            "first_name": "new_first_name",
            "last_name": "new_last_name",
            "birthdate": "2020-01-01",
        },
        bad_request={"first_name": 1},
    )

    test_retrieve = RetrieveModelViewTest(path_params=get_path_params)
    test_update = UpdateModelViewTest(
        path_params=get_path_params, body_params=employee_body_params
    )
    test_delete = DeleteModelViewTest(path_params=get_path_params)
