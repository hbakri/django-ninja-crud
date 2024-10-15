from typing import List

from ninja import Router

from examples import reusable_views
from examples.models import Department, Employee
from examples.schemas import DepartmentIn, DepartmentOut, EmployeeIn, EmployeeOut
from ninja_crud import views, viewsets

router = Router()


class DepartmentViewSet(viewsets.APIViewSet):
    router = router
    model = Department
    default_request_body = DepartmentIn
    default_response_body = DepartmentOut

    list_departments = views.ListView()
    create_department = views.CreateView()
    read_department = views.ReadView()
    update_department = views.UpdateView()
    delete_department = views.DeleteView()

    list_employees = views.ListView(
        path="/{id}/employees/",
        get_queryset=lambda request, path_parameters: Employee.objects.filter(
            department_id=path_parameters.id
        ),
        response_body=List[EmployeeOut],
    )
    create_employee = views.CreateView(
        path="/{id}/employees/",
        request_body=EmployeeIn,
        response_body=EmployeeOut,
        init_model=lambda request, path_parameters: Employee(
            department_id=path_parameters.id
        ),
    )

    reusable_read_department = reusable_views.ReusableReadView(
        model=Department,
        response_schema=DepartmentOut,
    )
    reusable_async_read_department = reusable_views.ReusableAsyncReadView(
        model=Department,
        response_schema=DepartmentOut,
    )
