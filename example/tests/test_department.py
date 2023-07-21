import uuid

from django.test import TestCase
from example.models import Department, Employee
from example.views.view_department import DepartmentViewSet

from ninja_crud.tests import (
    CreateModelViewTest,
    DeleteModelViewTest,
    ListModelViewTest,
    ModelViewSetTest,
    PathParameters,
    Payloads,
    RetrieveModelViewTest,
    UpdateModelViewTest,
)


class DepartmentViewSetTest(ModelViewSetTest, TestCase):
    model_view_set_class = DepartmentViewSet
    urls_prefix = "api/departments"

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

    test_list = ListModelViewTest()
    test_create = CreateModelViewTest(payloads=department_payloads)
    test_retrieve = RetrieveModelViewTest(path_parameters=get_path_parameters)
    test_update = UpdateModelViewTest(
        path_parameters=get_path_parameters, payloads=department_payloads
    )
    test_delete = DeleteModelViewTest(path_parameters=get_path_parameters)

    employee_payloads = Payloads(
        ok={
            "first_name": "new_first_name",
            "last_name": "new_last_name",
        },
        bad_request={"first_name": 1},
    )

    test_list_employees = ListModelViewTest(path_parameters=get_path_parameters)
    test_create_employee = CreateModelViewTest(
        path_parameters=get_path_parameters, payloads=employee_payloads
    )
