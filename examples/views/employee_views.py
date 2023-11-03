from ninja import Router

from examples.models import Employee
from examples.schemas import EmployeeIn, EmployeeOut
from ninja_crud import views
from ninja_crud.views import ModelViewSet

router = Router()


class EmployeeViewSet(ModelViewSet):
    model_class = Employee
    default_input_schema = EmployeeIn
    default_output_schema = EmployeeOut

    retrieve_view = views.RetrieveModelView()
    update_view = views.UpdateModelView()
    delete_view = views.DeleteModelView()


EmployeeViewSet.register_routes(router)
