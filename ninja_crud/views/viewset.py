from __future__ import annotations

from typing import Type

from django.db.models import Model
from ninja import Router

from ninja_crud.views import AbstractModelView


class ModelViewSetMeta(type):
    @staticmethod
    def validate_model_class(
        new_cls: ModelViewSetMeta,
    ):  # pragma: no cover
        cls_attr_name = "model_class"
        if not hasattr(new_cls, cls_attr_name):
            raise ValueError(
                f"{new_cls.__name__}.{cls_attr_name} class attribute must be set"
            )
        cls_attr_value = getattr(new_cls, cls_attr_name)
        if not isinstance(cls_attr_value, type) or not issubclass(
            cls_attr_value, Model
        ):
            raise ValueError(
                f"{new_cls.__name__}.{cls_attr_name} must be a subclass of django.db.models.Model"
            )

    def __new__(mcs, name, bases, attrs):
        new_cls = super().__new__(mcs, name, bases, attrs)

        if name != "ModelViewSet":
            mcs.validate_model_class(new_cls)

        return new_cls


class ModelViewSet(metaclass=ModelViewSetMeta):
    """
    A viewset offering CRUD operations for a Django model.

    Subclasses should specify the Django model via the `model_class` class attribute. You
    can then attach various views (subclasses of `AbstractModelView`) to the subclass to
    define the CRUD behavior.

    Attributes:
        - model_class (Type[Model]): The Django model class for CRUD operations.

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

    @classmethod
    def register_routes(cls, router: Router) -> None:
        """
        Registers the routes for this viewset with the given router.

        This method should be called after defining the viewset and before using the
        router.

        Args:
            router (Router): The Ninja Router to register the routes with.
        """
        for attr_name in dir(cls):
            attr_value = getattr(cls, attr_name)
            if isinstance(attr_value, AbstractModelView):
                attr_value.register_route(router, cls.model_class)
