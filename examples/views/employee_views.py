from ninja import Router

from examples.models import Employee
from examples.schemas import EmployeeIn, EmployeeOut
from ninja_crud import views, viewsets

router = Router()


class EmployeeViewSet(viewsets.ModelViewSet):
    model = Employee

    retrieve_employee = views.RetrieveModelView(output_schema=EmployeeOut)
    update_employee = views.UpdateModelView(
        input_schema=EmployeeIn, output_schema=EmployeeOut
    )
    delete_employee = views.DeleteModelView()


EmployeeViewSet.register_routes(router)
