from ninja import Router

from examples.models import Employee
from examples.schemas import EmployeeIn, EmployeeOut
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

    retrieve = RetrieveModelView(
        output_schema=output_schema,
        queryset_getter=lambda id: Employee.objects.select_related("department"),
    )
    update = UpdateModelView(
        input_schema=input_schema,
        output_schema=output_schema,
        pre_save=lambda request, instance: None,
        post_save=lambda request, instance: None,
    )
    delete = DeleteModelView()


router = Router()
EmployeeViewSet.register_routes(router)
