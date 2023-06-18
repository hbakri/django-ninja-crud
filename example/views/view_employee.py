from example.models import Employee
from example.schemas import EmployeeIn, EmployeeOut
from ninja import Router

from ninja_crud.views import (
    DeleteModelView,
    ModelViewSet,
    RetrieveModelView,
    UpdateModelView,
)


class EmployeeViewSet(ModelViewSet):
    model = Employee
    input_schema = EmployeeIn
    output_schema = EmployeeOut

    retrieve = RetrieveModelView(output_schema=output_schema)
    update = UpdateModelView(input_schema=input_schema, output_schema=output_schema)
    delete = DeleteModelView()


router = Router()
EmployeeViewSet.register_routes(router)
