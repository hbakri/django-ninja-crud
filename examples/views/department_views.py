from ninja import Router

from examples.models import Department, Employee
from examples.schemas import DepartmentIn, DepartmentOut, EmployeeIn, EmployeeOut
from ninja_crud import views, viewsets

router = Router()


class DepartmentViewSet(viewsets.ModelViewSet):
    model = Department
    default_payload_schema = DepartmentIn
    default_response_schema = DepartmentOut

    list_departments = views.ListModelView()
    create_department = views.CreateModelView()
    retrieve_department = views.RetrieveModelView()
    update_department = views.UpdateModelView()
    delete_department = views.DeleteModelView()

    list_employees = views.ListModelView(
        path="/{id}/employees/",
        queryset_getter=lambda id: Employee.objects.filter(department_id=id),
        response_schema=EmployeeOut,
    )
    create_employee = views.CreateModelView(
        path="/{id}/employees/",
        model_factory=lambda id: Employee(department_id=id),
        payload_schema=EmployeeIn,
        response_schema=EmployeeOut,
    )


DepartmentViewSet.register_routes(router)
