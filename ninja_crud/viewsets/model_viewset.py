import inspect
from typing import Optional, Type

from django.db.models import Model
from ninja import Router, Schema

from ninja_crud import utils
from ninja_crud.views import AbstractModelView


class ModelViewSet:
    """
    A viewset offering CRUD operations for a Django model.

    Subclasses should specify the Django model via the `model` class attribute. You
    can then attach various views (subclasses of `AbstractModelView`) to the subclass to
    define the CRUD behavior.

    Attributes:
        model (Type[Model]): The Django model class for CRUD operations.
        default_input_schema (Optional[Type[Schema]], optional): The default schema to use for
            deserializing the request payload. Defaults to None.
        default_output_schema (Optional[Type[Schema]], optional): The default schema to use for
            serializing the response payload. Defaults to None.

    Example:
    1. Define your `ModelViewSet` and register its routes:
    ```python
    # examples/views/department_views.py
    from django.http import HttpRequest
    from ninja import Router
    from ninja_crud import views, viewsets

    from examples.models import Department
    from examples.schemas import DepartmentIn, DepartmentOut

    router = Router()

    class DepartmentViewSet(viewsets.ModelViewSet):
        model = Department

        list_view = views.ListModelView(output_schema=DepartmentOut)
        create_view = views.CreateModelView(input_schema=DepartmentIn, output_schema=DepartmentOut)
        retrieve_view = views.RetrieveModelView(output_schema=DepartmentOut)
        update_view = views.UpdateModelView(input_schema=DepartmentIn, output_schema=DepartmentOut)
        delete_view = views.DeleteModelView()

    # The register_routes method must be called to register the routes
    DepartmentViewSet.register_routes(router)

    # Beyond the CRUD operations managed by the viewset,
    # the router can be used in the standard Django Ninja way
    @router.get("/statistics/", response=dict)
    def retrieve_department_statistics(request: HttpRequest):
        return {"total": Department.objects.count()}
    ```

    2. Include your router in your Ninja API configuration:
    ```python
    # config/api.py
    from ninja import NinjaAPI
    from examples.views.department_views import router as department_router

    api = NinjaAPI(...)
    api.add_router("departments", department_router)
    ```

    Note:
        The `register_routes` method must be called to register the CRUD endpoints
        with a Ninja router. This should be done after defining the viewset.
    """

    model: Type[Model]
    default_input_schema: Optional[Type[Schema]]
    default_output_schema: Optional[Type[Schema]]

    def __init_subclass__(cls, **kwargs):
        """
        Special method in Python that is automatically called when a class is subclassed.

        For `ModelViewSet` subclasses, this method validates the class attributes and binds
        the views to the subclass. It should not be called directly.
        """
        super().__init_subclass__(**kwargs)

        if hasattr(cls, "model"):
            cls._validate_model_class()
            cls._validate_input_schema_class(optional=True)
            cls._validate_output_schema_class(optional=True)
            cls._bind_model_views()

    @classmethod
    def _bind_model_views(cls):
        """
        Binds instances of `AbstractModelView` to the ModelViewSet subclass.

        This allows the views to access the ModelViewSet subclass via the `viewset_class`
        attribute, and access default schemas via the `default_input_schema` and
        `default_output_schema` attributes.

        Note:
            This method is called automatically during the subclass initialization of
            `ModelViewSet`. It should not be called directly.
        """
        for attr_name, attr_value in inspect.getmembers(cls):
            if isinstance(attr_value, AbstractModelView):
                attr_value.bind_to_viewset(cls, model_view_name=attr_name)

    @classmethod
    def register_routes(cls, router: Router) -> None:
        """
        Register the routes with the given Ninja Router.

        This method should be called after all the views have been attached to the
        ModelViewSet subclass.

        Parameters:
            router (Router): The Ninja Router to register the routes with.
        """
        for _, attr_value in inspect.getmembers(cls):
            if isinstance(attr_value, AbstractModelView):
                attr_value.register_route(router, cls.model)

    @classmethod
    def _validate_model_class(cls) -> None:
        """
        Validates that the `model` attribute is a subclass of `Model`.

        Raises:
            - ValueError: If the attribute is not set.
            - TypeError: If the attribute is not a subclass of `Model`.
        """
        utils.validate_class_attribute_type(cls, "model", expected_type=Type[Model])

    @classmethod
    def _validate_input_schema_class(cls, optional: bool = True) -> None:
        """
        Validates that the `default_input_schema` attribute is a subclass of `Schema`.

        Parameters:
            - optional (bool, optional): Whether the attribute is optional. Defaults to `True`.

        Raises:
            - ValueError: If the attribute is not optional and is not set.
            - TypeError: If the attribute is not a subclass of `Schema`.
        """
        utils.validate_class_attribute_type(
            cls, "default_input_schema", expected_type=Type[Schema], optional=optional
        )

    @classmethod
    def _validate_output_schema_class(cls, optional: bool = True) -> None:
        """
        Validates that the `default_output_schema` attribute is a subclass of `Schema`.

        Parameters:
            - optional (bool, optional): Whether the attribute is optional. Defaults to `True`.

        Raises:
            - ValueError: If the attribute is not optional and is not set.
            - TypeError: If the attribute is not a subclass of `Schema`.
        """
        utils.validate_class_attribute_type(
            cls, "default_output_schema", expected_type=Type[Schema], optional=optional
        )
