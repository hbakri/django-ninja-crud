import uuid
from http import HTTPStatus

from rest_testing import APITestCase, APIViewTestScenario

from examples.models import Department, Employee
from examples.schemas import DepartmentOut, EmployeeOut, Paged


class TestDepartmentViewSet(APITestCase):
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

    def test_list_departments(self):
        self.assertScenariosSucceed(
            method="GET",
            path="/api/departments/",
            scenarios=[
                APIViewTestScenario(
                    expected_response_status=HTTPStatus.OK,
                    expected_response_body_type=Paged[DepartmentOut],
                ),
            ],
        )

    def test_create_department(self):
        self.assertScenariosSucceed(
            method="POST",
            path="/api/departments/",
            scenarios=[
                APIViewTestScenario(
                    request_body={"title": "new_title"},
                    expected_response_status=HTTPStatus.CREATED,
                    expected_response_body_type=DepartmentOut,
                ),
                APIViewTestScenario(
                    request_body={"title": "department-1"},
                    expected_response_status=HTTPStatus.CONFLICT,
                ),
                APIViewTestScenario(
                    request_body={"title": [1]},
                    expected_response_status=HTTPStatus.BAD_REQUEST,
                ),
            ],
        )

    def test_read_department(self):
        self.assertScenariosSucceed(
            method="GET",
            path="/api/departments/{id}",
            scenarios=[
                APIViewTestScenario(
                    path_parameters={"id": self.department_1.id},
                    expected_response_status=HTTPStatus.OK,
                    expected_response_body_type=DepartmentOut,
                    expected_response_body={
                        "id": str(self.department_1.id),
                        "title": self.department_1.title,
                    },
                ),
                APIViewTestScenario(
                    path_parameters={"id": uuid.uuid4()},
                    expected_response_status=HTTPStatus.NOT_FOUND,
                ),
            ],
        )

    def test_update_department(self):
        self.assertScenariosSucceed(
            method="PUT",
            path="/api/departments/{id}",
            scenarios=[
                APIViewTestScenario(
                    path_parameters={"id": self.department_1.id},
                    request_body={"title": "new_title"},
                    expected_response_status=HTTPStatus.OK,
                    expected_response_body_type=DepartmentOut,
                    expected_response_body={
                        "id": str(self.department_1.id),
                        "title": "new_title",
                    },
                ),
                APIViewTestScenario(
                    path_parameters={"id": uuid.uuid4()},
                    request_body={"title": "new_title"},
                    expected_response_status=HTTPStatus.NOT_FOUND,
                ),
                APIViewTestScenario(
                    path_parameters={"id": self.department_1.id},
                    request_body={"title": [1]},
                    expected_response_status=HTTPStatus.BAD_REQUEST,
                ),
                APIViewTestScenario(
                    path_parameters={"id": self.department_1.id},
                    request_body={"title": self.department_2.title},
                    expected_response_status=HTTPStatus.CONFLICT,
                ),
            ],
        )

    def test_delete_department(self):
        self.assertScenariosSucceed(
            method="DELETE",
            path="/api/departments/{id}",
            scenarios=[
                APIViewTestScenario(
                    path_parameters={"id": self.department_1.id},
                    expected_response_status=HTTPStatus.NO_CONTENT,
                    expected_response_body=b"",
                ),
                APIViewTestScenario(
                    path_parameters={"id": uuid.uuid4()},
                    expected_response_status=HTTPStatus.NOT_FOUND,
                ),
            ],
        )

    def test_list_employees(self):
        self.assertScenariosSucceed(
            method="GET",
            path="/api/departments/{id}/employees/",
            scenarios=[
                APIViewTestScenario(
                    path_parameters={"id": self.department_1.id},
                    expected_response_status=HTTPStatus.OK,
                    expected_response_body_type=Paged[EmployeeOut],
                ),
            ],
        )

    def test_create_employee(self):
        self.assertScenariosSucceed(
            method="POST",
            path="/api/departments/{id}/employees/",
            scenarios=[
                APIViewTestScenario(
                    path_parameters={"id": self.department_1.id},
                    request_body={
                        "first_name": "first_name",
                        "last_name": "last_name",
                    },
                    expected_response_status=HTTPStatus.CREATED,
                    expected_response_body_type=EmployeeOut,
                ),
                APIViewTestScenario(
                    path_parameters={"id": self.department_1.id},
                    request_body={"first_name": "first_name"},
                    expected_response_status=HTTPStatus.BAD_REQUEST,
                ),
            ],
        )

    def test_reusable_read_department(self):
        self.assertScenariosSucceed(
            method="GET",
            path="/api/departments/{id}/reusable",
            scenarios=[
                APIViewTestScenario(
                    path_parameters={"id": self.department_1.id},
                    expected_response_status=HTTPStatus.OK,
                    expected_response_body_type=DepartmentOut,
                    expected_response_body={
                        "id": str(self.department_1.id),
                        "title": self.department_1.title,
                    },
                ),
                APIViewTestScenario(
                    path_parameters={"id": uuid.uuid4()},
                    expected_response_status=HTTPStatus.NOT_FOUND,
                ),
            ],
        )

    def test_reusable_async_read_department(self):
        self.assertScenariosSucceed(
            method="GET",
            path="/api/departments/{id}/reusable/async",
            scenarios=[
                APIViewTestScenario(
                    path_parameters={"id": self.department_1.id},
                    expected_response_status=HTTPStatus.OK,
                    expected_response_body_type=DepartmentOut,
                    expected_response_body={
                        "id": str(self.department_1.id),
                        "title": self.department_1.title,
                    },
                ),
                APIViewTestScenario(
                    path_parameters={"id": uuid.uuid4()},
                    expected_response_status=HTTPStatus.NOT_FOUND,
                ),
            ],
        )
