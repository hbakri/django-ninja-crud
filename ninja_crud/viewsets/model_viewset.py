import inspect
from typing import Optional, Type

from django.db.models import Model
from ninja import Router, Schema

from ninja_crud.views import AbstractModelView


class ModelViewSet:
    """
    A viewset offering CRUD (Create, Read, Update, Delete) operations for a Django
    model. It serves as a foundational class for defining model-specific viewsets with
    tailored CRUD behavior. By subclassing `ModelViewSet` and attaching
    `AbstractModelView` subclasses, you create a cohesive API for interacting with a
    model's data.

    Attributes:
        model (Type[Model]): The Django model associated with the viewset.
        default_request_body (Optional[Type[Schema]], optional): The default schema
            for deserializing the request body. Defaults to None.
        default_response_body (Optional[Type[Schema]], optional): The default schema
            for serializing the response body. Defaults to None.

    Usage:
        Define a `ModelViewSet` subclass, specify the model, and attach CRUD view
        instances. Finally, use `register_routes` to add the configured routes to a
        Ninja router, integrating the viewset with your API.

    Example Usage:
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
    """

    model: Type[Model]
    default_request_body: Optional[Type[Schema]]
    default_response_body: Optional[Type[Schema]]

    def __init_subclass__(cls, *args, **kwargs) -> None:
        super().__init_subclass__(*args, **kwargs)

        if hasattr(cls, "model"):
            cls._bind_model_views()

    @classmethod
    def _bind_model_views(cls) -> None:
        """
        Automatically binds `AbstractModelView` instances to the subclass, enabling
        them to access model and schema information defined in the `ModelViewSet`.
        This method is internally called and should not be used directly.
        """
        for _, model_view in inspect.getmembers(
            cls, lambda member: isinstance(member, AbstractModelView)
        ):
            model_view.model_viewset_class = cls

    @classmethod
    def register_routes(cls, router: Router) -> None:
        """
        Registers the CRUD operation routes with a Ninja Router. This method organizes
        the routes based on their definition order within the subclass, maintaining a
        logical API structure. The route names and operation IDs are derived from the
        attribute names of the `AbstractModelView` instances, ensuring consistent and
        easily identifiable routes in the OpenAPI schema.

        Args:
            router (ninja.Router): The Ninja Router to which the routes will be added.
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
