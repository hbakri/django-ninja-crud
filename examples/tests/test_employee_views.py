import uuid

from examples.models import Department, Employee
from examples.views.employee_views import EmployeeViewSet
from ninja_crud.testing.core.components import PathParameters, Payloads
from ninja_crud.testing.views import (
    DeleteModelViewTest,
    RetrieveModelViewTest,
    UpdateModelViewTest,
)
from ninja_crud.testing.viewsets import ModelViewSetTestCase


class TestEmployeeViewSet(ModelViewSetTestCase):
    model_viewset_class = EmployeeViewSet
    base_path = "api/employees"

    department_1: Department
    department_2: Department
    employee: Employee

    @classmethod
    def setUpTestData(cls):
        cls.department_1 = Department.objects.create(title="department-1")
        cls.department_2 = Department.objects.create(title="department-2")
        cls.employee = Employee.objects.create(
            first_name="first_name", last_name="last_name", department=cls.department_1
        )

    def get_path_parameters(self):
        return PathParameters(
            ok={"id": self.employee.id}, not_found={"id": uuid.uuid4()}
        )

    employee_payloads = Payloads(
        ok={
            "first_name": "new_first_name",
            "last_name": "new_last_name",
            "birthdate": "2020-01-01",
        },
        bad_request={"first_name": 1},
    )

    test_retrieve_view = RetrieveModelViewTest(path_parameters=get_path_parameters)
    test_update_view = UpdateModelViewTest(
        path_parameters=get_path_parameters, payloads=employee_payloads
    )
    test_delete_view = DeleteModelViewTest(path_parameters=get_path_parameters)
