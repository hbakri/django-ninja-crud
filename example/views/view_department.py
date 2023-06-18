from example.models import Department, Employee
from example.schemas import DepartmentIn, DepartmentOut, EmployeeIn, EmployeeOut
from ninja import Router

from ninja_crud.views import (
    CreateModelView,
    DeleteModelView,
    ListModelView,
    ModelViewSet,
    RetrieveModelView,
    UpdateModelView,
)


class DepartmentViewSet(ModelViewSet):
    model = Department
    input_schema = DepartmentIn
    output_schema = DepartmentOut

    list = ListModelView(output_schema=output_schema)
    create = CreateModelView(input_schema=input_schema, output_schema=output_schema)
    retrieve = RetrieveModelView(output_schema=output_schema)
    update = UpdateModelView(input_schema=input_schema, output_schema=output_schema)
    delete = DeleteModelView()

    list_employees = ListModelView(
        detail=True,
        related_model=Employee,
        output_schema=EmployeeOut,
        queryset_getter=lambda id: Employee.objects.filter(department_id=id),
    )
    create_employee = CreateModelView(
        detail=True,
        related_model=Employee,
        input_schema=EmployeeIn,
        output_schema=EmployeeOut,
        pre_save=lambda request, id, instance: setattr(instance, "department_id", id),
    )


router = Router()
DepartmentViewSet.register_routes(router)
