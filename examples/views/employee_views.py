from ninja import Router

from examples.models import Employee
from examples.schemas import EmployeeIn, EmployeeOut
from ninja_crud import views, viewsets

router = Router()


class EmployeeViewSet(viewsets.ModelViewSet):
    model = Employee

    retrieve_employee = views.RetrieveModelView(response_body=EmployeeOut)
    update_employee = views.UpdateModelView(
        request_body=EmployeeIn, response_body=EmployeeOut
    )
    delete_employee = views.DeleteModelView()


EmployeeViewSet.register_routes(router)
