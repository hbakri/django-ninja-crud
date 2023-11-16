from typing import Type

from ninja import Schema

from ninja_crud.views import (
    CreateModelView,
    DeleteModelView,
    ListModelView,
    RetrieveModelView,
    UpdateModelView,
)
from ninja_crud.viewsets.model_viewset import ModelViewSet


class BaseModelViewSet(ModelViewSet):
    """
    Provides a generic viewset with basic CRUD operations for a Django model.

    This viewset is designed to be subclassed for specific Django models, providing a
    standardized way to perform create, read, update, and delete operations. It expects
    the subclasses to define the associated Django model and the input/output schemas
    for serialization and deserialization of data.

    Attributes:
        model (Type[Model]): The Django model class for CRUD operations.
        default_input_schema (Type[Schema]): The default schema to use for
            deserializing the request payload.
        default_output_schema (Type[Schema]): The default schema to use for
            serializing the response payload.
        list_view (ListModelView): The view to use for listing model instances.
        create_view (CreateModelView): The view to use for creating model instances.
        retrieve_view (RetrieveModelView): The view to use for retrieving model
            instances.
        update_view (UpdateModelView): The view to use for updating model instances.
        delete_view (DeleteModelView): The view to use for deleting model instances.

    Example:
    ```python
    from ninja import Router
    from ninja_crud import viewsets

    from examples.models import Department
    from examples.schemas import DepartmentIn, DepartmentOut

    router = Router()

    class DepartmentViewSet(viewsets.BaseModelViewSet):
        model = Department
        default_input_schema = DepartmentIn
        default_output_schema = DepartmentOut

    DepartmentViewSet.register_routes(router)
    ```

    It is the exact equivalent and shorthand for the following:
    ```python
    from ninja import Router
    from ninja_crud import views, viewsets

    from examples.models import Department
    from examples.schemas import DepartmentIn, DepartmentOut

    router = Router()

    class DepartmentViewSet(viewsets.ModelViewSet):
        model = Department
        default_input_schema = DepartmentIn
        default_output_schema = DepartmentOut

        list_view = views.ListModelView()
        create_view = views.CreateModelView()
        retrieve_view = views.RetrieveModelView()
        update_view = views.UpdateModelView()
        delete_view = views.DeleteModelView()

    DepartmentViewSet.register_routes(router)
    ```

    Note:
        The `register_routes` method must be called to register the CRUD endpoints
        with a Ninja router. This should be done after defining the viewset.
    """

    default_input_schema: Type[Schema]
    default_output_schema: Type[Schema]

    list_view = ListModelView()
    create_view = CreateModelView()
    retrieve_view = RetrieveModelView()
    update_view = UpdateModelView()
    delete_view = DeleteModelView()

    def __init_subclass__(cls, **kwargs):
        """
        Special method in Python that is automatically called when a class is subclassed.

        For `BaseModelViewSet` subclasses, this method validates the class attributes and binds
        the views to the subclass. It should not be called directly.
        """
        super().__init_subclass__(**kwargs)
        cls._validate_input_schema_class(optional=False)
        cls._validate_output_schema_class(optional=False)
