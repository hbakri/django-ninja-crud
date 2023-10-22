from typing import Type

from ninja import Schema

from ninja_crud.views import (
    CreateModelView,
    DeleteModelView,
    ListModelView,
    ModelViewSet,
    RetrieveModelView,
    UpdateModelView,
)


class BaseModelViewSet(ModelViewSet):
    """
    A viewset offering basic CRUD operations for a Django model.

    Subclasses should specify the Django model via the `model_class` class attribute. You
    also need to specify the default input and output schemas via the `default_input_schema`
    and `default_output_schema` class attributes, respectively.

    Attributes:
        - model_class (Type[Model]): The Django model class for CRUD operations.
        - default_input_schema (Type[Schema]): The default schema to use for
            deserializing the request payload.
        - default_output_schema (Type[Schema]): The default schema to use for
            serializing the response payload.

    Example:
    ```python
    from ninja import Router
    from django.http import HttpRequest
    from ninja_crud.viewsets import BaseModelViewSet
    from example.models import Department
    from example.schemas import DepartmentIn, DepartmentOut

    router = Router()

    class DepartmentViewSet(BaseModelViewSet):
        model_class = Department
        default_input_schema = DepartmentIn
        default_output_schema = DepartmentOut

    DepartmentViewSet.register_routes(router)

    # The router can then be used as normal
    @router.get("/{name}", response=DepartmentOut)
    def get_department_by_name(request: HttpRequest, name: str):
        return Department.objects.get(name=name)
    ```
    """

    default_input_schema: Type[Schema]
    default_output_schema: Type[Schema]

    list_view = ListModelView()
    create_view = CreateModelView()
    retrieve_view = RetrieveModelView()
    update_view = UpdateModelView()
    delete_view = DeleteModelView()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.validate_input_schema_class(optional=False)
        cls.validate_output_schema_class(optional=False)
