from typing import List

from ninja import Router

from examples.models import Department, Employee
from examples.schemas import DepartmentIn, DepartmentOut, EmployeeIn, EmployeeOut
from ninja_crud import views, viewsets

router = Router()


class DepartmentViewSet(viewsets.ModelViewSet):
    model = Department
    default_request_body = DepartmentIn
    default_response_body = DepartmentOut

    list_departments = views.ListModelView()
    create_department = views.CreateModelView()
    retrieve_department = views.RetrieveModelView()
    update_department = views.UpdateModelView()
    delete_department = views.DeleteModelView()

    list_employees = views.ListModelView(
        path="/{id}/employees/",
        get_queryset=lambda path_parameters: Employee.objects.filter(
            department_id=getattr(path_parameters, "id", None)
        ),
        response_body=List[EmployeeOut],
    )
    create_employee = views.CreateModelView(
        path="/{id}/employees/",
        request_body=EmployeeIn,
        response_body=EmployeeOut,
        create_model=lambda request, path_parameters: Employee(
            department_id=getattr(path_parameters, "id", None)
        ),
    )


DepartmentViewSet.register_routes(router)
