from ninja import Router

from examples.models import Department, Employee
from examples.schemas import DepartmentIn, DepartmentOut, EmployeeIn, EmployeeOut
from ninja_crud import views, viewsets

router = Router()


class DepartmentViewSet(viewsets.BaseModelViewSet):
    model_class = Department
    default_input_schema = DepartmentIn
    default_output_schema = DepartmentOut

    list_employees_view = views.ListModelView(
        detail=True,
        queryset_getter=lambda id: Employee.objects.filter(department_id=id),
        output_schema=EmployeeOut,
    )
    create_employee_view = views.CreateModelView(
        detail=True,
        model_factory=lambda id: Employee(department_id=id),
        input_schema=EmployeeIn,
        output_schema=EmployeeOut,
    )


DepartmentViewSet.register_routes(router)
