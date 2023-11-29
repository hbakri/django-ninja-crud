import uuid

from examples.models import Department, Employee
from examples.views.department_views import DepartmentViewSet
from ninja_crud import testing


class TestDepartmentViewSet(testing.viewsets.ModelViewSetTestCase):
    model_viewset_class = DepartmentViewSet
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

    @property
    def path_parameters(self):
        return testing.components.PathParameters(
            ok={"id": self.department_1.id}, not_found={"id": uuid.uuid4()}
        )

    department_payloads = testing.components.Payloads(
        ok={"title": "new_title"},
        bad_request={"bad-title": 1},
        conflict={"title": "department-2"},
    )

    test_list_view = testing.views.ListModelViewTest()
    test_create_view = testing.views.CreateModelViewTest(payloads=department_payloads)
    test_retrieve_view = testing.views.RetrieveModelViewTest(path_parameters)
    test_update_view = testing.views.UpdateModelViewTest(
        path_parameters, payloads=department_payloads
    )
    test_delete_view = testing.views.DeleteModelViewTest(path_parameters)

    employee_payloads = testing.components.Payloads(
        ok={
            "first_name": "new_first_name",
            "last_name": "new_last_name",
        },
        bad_request={"first_name": 1},
    )

    test_list_employees_view = testing.views.ListModelViewTest(
        path_parameters=path_parameters
    )
    test_create_employee_view = testing.views.CreateModelViewTest(
        path_parameters=path_parameters, payloads=employee_payloads
    )
