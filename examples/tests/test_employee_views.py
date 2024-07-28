import uuid
from http import HTTPStatus

from rest_testing import APITestCase, APIViewTestScenario

from examples.models import Department, Employee
from examples.schemas import EmployeeOut


class TestEmployeeViewSet(APITestCase):
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

    def test_read_employee(self):
        self.assertScenariosSucceed(
            method="GET",
            path="/api/employees/{id}",
            scenarios=[
                APIViewTestScenario(
                    path_parameters={"id": self.employee.id},
                    expected_response_status=HTTPStatus.OK,
                    expected_response_body_type=EmployeeOut,
                    expected_response_body=EmployeeOut.from_orm(self.employee).json(),
                ),
                APIViewTestScenario(
                    path_parameters={"id": uuid.uuid4()},
                    expected_response_status=HTTPStatus.NOT_FOUND,
                ),
            ],
        )

    def test_update_employee(self):
        self.assertScenariosSucceed(
            method="PUT",
            path="/api/employees/{id}",
            scenarios=[
                APIViewTestScenario(
                    path_parameters={"id": self.employee.id},
                    request_body={"first_name": "new_name", "last_name": "new_name"},
                    expected_response_status=HTTPStatus.OK,
                    expected_response_body={
                        "id": str(self.employee.id),
                        "first_name": "new_name",
                        "last_name": "new_name",
                        "birthdate": self.employee.birthdate,
                        "department_id": str(self.employee.department_id),
                    },
                ),
                APIViewTestScenario(
                    path_parameters={"id": uuid.uuid4()},
                    request_body={"first_name": "new_name", "last_name": "new_name"},
                    expected_response_status=HTTPStatus.NOT_FOUND,
                ),
                APIViewTestScenario(
                    path_parameters={"id": self.employee.id},
                    request_body={"bad-title": "bad-value"},
                    expected_response_status=HTTPStatus.BAD_REQUEST,
                ),
            ],
        )

    def test_delete_employee(self):
        self.assertScenariosSucceed(
            method="DELETE",
            path="/api/employees/{id}",
            scenarios=[
                APIViewTestScenario(
                    path_parameters={"id": self.employee.id},
                    expected_response_status=HTTPStatus.NO_CONTENT,
                    expected_response_body=b"",
                ),
                APIViewTestScenario(
                    path_parameters={"id": uuid.uuid4()},
                    expected_response_status=HTTPStatus.NOT_FOUND,
                ),
            ],
        )
