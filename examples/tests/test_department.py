from typing import Union

from django.test import TestCase

from examples.models import Department, Employee
from examples.views.view_department import DepartmentViewSet
from ninja_crud.tests import (
    CreateModelViewTest,
    Credentials,
    DeleteModelViewTest,
    ListModelViewTest,
    ModelViewSetTest,
    Payloads,
    RetrieveModelViewTest,
    UpdateModelViewTest,
)


class DepartmentViewSetTest(ModelViewSetTest, TestCase):
    model_view_set = DepartmentViewSet
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

    def get_instance(self: Union["DepartmentViewSetTest", TestCase]):
        return self.department_1

    def get_credentials(self: Union["DepartmentViewSetTest", TestCase]):
        return Credentials(
            ok={"HTTP_AUTHORIZATION": f"Bearer {self.token}"}, unauthorized={}
        )

    department_payloads = Payloads(
        ok={"title": "new_title"},
        bad_request={"bad-title": 1},
        conflict={"title": "department-2"},
    )

    test_list = ListModelViewTest(
        instance_getter=get_instance,
        credentials_getter=get_credentials,
    )
    test_create = CreateModelViewTest(
        payloads=department_payloads,
        instance_getter=get_instance,
        credentials_getter=get_credentials,
    )
    test_retrieve = RetrieveModelViewTest(
        instance_getter=get_instance,
        credentials_getter=get_credentials,
    )
    test_update = UpdateModelViewTest(
        payloads=department_payloads,
        instance_getter=get_instance,
        credentials_getter=get_credentials,
    )
    test_delete = DeleteModelViewTest(
        instance_getter=get_instance, credentials_getter=get_credentials
    )

    employee_payloads = Payloads(
        ok={
            "first_name": "new_first_name",
            "last_name": "new_last_name",
        },
        bad_request={"first_name": 1},
    )

    test_list_employees = ListModelViewTest(
        instance_getter=get_instance,
        credentials_getter=get_credentials,
    )
    test_create_employee = CreateModelViewTest(
        payloads=employee_payloads,
        instance_getter=get_instance,
        credentials_getter=get_credentials,
    )
