from __future__ import annotations

from typing import Any, Optional, Type

from django.db.models import Model
from ninja import Router, Schema

from ninja_crud import utils
from ninja_crud.views import AbstractModelView


class ModelViewSet:
    """
    A viewset offering CRUD operations for a Django model.

    Subclasses should specify the Django model via the `model_class` class attribute. You
    can then attach various views (subclasses of `AbstractModelView`) to the subclass to
    define the CRUD behavior.

    Attributes:
        - model_class (Type[Model]): The Django model class for CRUD operations.
        - default_input_schema (Optional[Type[Schema]], optional): The default schema to use for
            deserializing the request payload. Defaults to None.
        - default_output_schema (Optional[Type[Schema]], optional): The default schema to use for
            serializing the response payload. Defaults to None.

    Example:
    ```python
    # example/views.py
    from ninja import Router
    from django.http import HttpRequest
    from ninja_crud.views import (
        CreateModelView,
        DeleteModelView,
        ListModelView,
        ModelViewSet,
        RetrieveModelView,
        UpdateModelView,
    )
    from example.models import Department
    from example.schemas import DepartmentIn, DepartmentOut

    router = Router()

    class DepartmentViewSet(ModelViewSet):
        model_class = Department

        # AbstractModelView subclasses can be used as-is
        list = ListModelView(output_schema=DepartmentOut)
        create = CreateModelView(input_schema=DepartmentIn, output_schema=DepartmentOut)
        retrieve = RetrieveModelView(output_schema=DepartmentOut)
        update = UpdateModelView(input_schema=DepartmentIn, output_schema=DepartmentOut)
        delete = DeleteModelView()

    # The register_routes method must be called to register the routes with the router
    DepartmentViewSet.register_routes(router)

    # The router can then be used as normal
    @router.get("/{name}", response=DepartmentOut)
    def get_department_by_name(request: HttpRequest, name: str):
        return Department.objects.get(name=name)
    ```

    And then in your `api.py` file:
    ```python
    # example/api.py
    from ninja import NinjaAPI
    from example.views import router as department_router

    api = NinjaAPI(...)
    api.add_router("departments", department_router)
    ```
    """

    model_class: Type[Model]
    default_input_schema: Optional[Type[Schema]]
    default_output_schema: Optional[Type[Schema]]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if hasattr(cls, "model_class"):
            cls._validate_model_class()
            cls._validate_input_schema_class(optional=True)
            cls._validate_output_schema_class(optional=True)
            cls.bind_model_views()

    @classmethod
    def bind_model_views(cls):
        def bind_model_view(attr_name: str, attr_value: Any):
            if isinstance(attr_value, AbstractModelView):
                attr_value.bind_to_viewset(cls, model_view_name=attr_name)

        utils.iterate_class_attributes(cls, func=bind_model_view)

    @classmethod
    def register_routes(cls, router: Router) -> None:
        """
        Register the routes with the given Ninja Router.

        This method should be called after all the views have been attached to the
        ModelViewSet subclass.

        Args:
            router (Router): The Ninja Router to register the routes with.
        """

        def register_model_view_route(attr_name: str, attr_value: Any):
            if isinstance(attr_value, AbstractModelView):
                attr_value.register_route(router, cls.model_class)

        utils.iterate_class_attributes(cls, func=register_model_view_route)

    @classmethod
    def _validate_class_attribute(
        cls, attr_name: str, expected_type: Type, optional: bool = False
    ) -> None:
        attr_value = getattr(cls, attr_name, None)
        if attr_value is None:
            if optional:
                return
            else:
                raise ValueError(
                    f"{cls.__name__}.{attr_name} class attribute must be set"
                )
        if not isinstance(attr_value, type) or not issubclass(
            attr_value, expected_type
        ):
            raise ValueError(
                f"{cls.__name__}.{attr_name} must be an instance of {expected_type.__name__}"
            )

    @classmethod
    def _validate_model_class(cls) -> None:
        return cls._validate_class_attribute("model_class", expected_type=Model)

    @classmethod
    def _validate_input_schema_class(cls, optional: bool = True) -> None:
        return cls._validate_class_attribute(
            "default_input_schema", expected_type=Schema, optional=optional
        )

    @classmethod
    def _validate_output_schema_class(cls, optional: bool = True) -> None:
        return cls._validate_class_attribute(
            "default_output_schema", expected_type=Schema, optional=optional
        )
