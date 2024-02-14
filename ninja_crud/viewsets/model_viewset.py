import inspect
from typing import Optional, Type

from django.db.models import Model
from ninja import Router, Schema

from ninja_crud.views import AbstractModelView


class ModelViewSet:
    """
    A viewset offering CRUD operations for a Django model.

    Subclasses should specify the Django model via the `model` class attribute. You
    can then attach various views (subclasses of `AbstractModelView`) to the subclass to
    define the CRUD behavior.

    Attributes:
        model (Type[Model]): The Django model class for CRUD operations.
        default_request_body (Optional[Type[Schema]], optional): The default schema to use for
            deserializing the request payload. Defaults to None.
        default_response_body (Optional[Type[Schema]], optional): The default schema to use for
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

        list_departments = views.ListModelView(response_body=DepartmentOut)
        create_department = views.CreateModelView(request_body=DepartmentIn, response_body=DepartmentOut)
        retrieve_department = views.RetrieveModelView(response_body=DepartmentOut)
        update_department = views.UpdateModelView(request_body=DepartmentIn, response_body=DepartmentOut)
        delete_department = views.DeleteModelView()

    # The register_routes method must be called to register the routes
    DepartmentViewSet.register_routes(router)

    # Beyond the CRUD operations managed by the viewset,
    # the router can be used in the standard Django Ninja way
    @router.get("/statistics/")
    def get_department_statistics(request: HttpRequest):
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
    default_request_body: Optional[Type[Schema]]
    default_response_body: Optional[Type[Schema]]

    def __init_subclass__(cls, **kwargs):
        """
        Special method in Python that is automatically called when a class is subclassed.

        For `ModelViewSet` subclasses, this method validates the class attributes and binds
        the views to the subclass. It should not be called directly.
        """
        super().__init_subclass__(**kwargs)

        if hasattr(cls, "model"):
            cls._bind_model_views()

    @classmethod
    def _bind_model_views(cls):
        """
        Binds instances of `AbstractModelView` to the ModelViewSet subclass.

        This allows the views to access the ModelViewSet subclass via the
        `model_viewset_class` attribute.

        Note:
            This method is called automatically during the subclass initialization of
            `ModelViewSet`. It should not be called directly.
        """
        for _, view_model in inspect.getmembers(cls):
            if isinstance(view_model, AbstractModelView):
                view_model.model_viewset_class = cls

    @classmethod
    def register_routes(cls, router: Router) -> None:
        """
        Register the routes with the given Ninja Router in the order they were defined.

        This method should be called after all the views have been attached to the
        ModelViewSet subclass.

        Parameters:
            router (Router): The Ninja Router to register the routes with.
        """
        view_attributes = {
            name: view
            for name, view in inspect.getmembers(cls)
            if isinstance(view, AbstractModelView)
        }

        attribute_order = list(cls.__dict__)
        ordered_view_attributes = sorted(
            view_attributes.items(), key=lambda item: attribute_order.index(item[0])
        )
        for name, view in ordered_view_attributes:
            view.register_route(router, route_name=name)
