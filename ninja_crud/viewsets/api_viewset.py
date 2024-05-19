import inspect
from typing import Any, Optional, Type, Union

import django.db.models
import ninja
import pydantic

from ninja_crud import views


class APIViewSet:
    """
    Declarative class for grouping related API views together in Django Ninja.

    This class simplifies the process of registering multiple API views for a single
    model by allowing you to define them as class attributes. It provides a framework
    for grouping related views together and automatically registers these views with
    the API or router when the class is defined.

    To register views with an API or router, you can either set the `api` or `router`
    attribute to the `NinjaAPI` or `Router` instance, respectively, or call the
    `add_views_to` method manually after the class is defined.

    Attributes:
        api (Optional[ninja.NinjaAPI], optional): The `NinjaAPI` instance to which
            views are registered if provided. Defaults to None.
        router (Optional[ninja.Router], optional): The `Router` instance to which
            views are registered if provided. Defaults to None.
        model (Optional[Type[django.db.models.Model]], optional): The Django model
            associated with the viewset. This can be used to automatically resolve
            path parameters and other model-specific configurations. Defaults to None.
        default_request_body (Optional[Type[pydantic.BaseModel]], optional): The
            default request body schema used for views in the viewset. Defaults to None.
        default_response_body (Optional[Type[Any]], optional): The default response
            body schema used for views in the viewset. Defaults to None.

    Example:
    ```python
    from ninja import Router
    from ninja_crud import views, viewsets

    from examples.models import Department
    from examples.schemas import DepartmentIn, DepartmentOut

    router = Router()


    # Example usage with a `Router` instance as class attribute:
    class DepartmentViewSet(viewsets.APIViewSet):
        router = router
        model = Department

        list_departments = views.ListView(response_body=List[DepartmentOut])
        create_department = views.CreateView(
            request_body=DepartmentIn,
            response_body=DepartmentOut,
        )
        read_department = views.ReadView(response_body=DepartmentOut)
        update_department = views.UpdateView(
            request_body=DepartmentIn,
            response_body=DepartmentOut,
        )
        delete_department = views.DeleteView()


    # Other example usage with refactored request and response bodies:
    class DepartmentViewSet(viewsets.APIViewSet):
        router = router
        model = Department
        default_request_body = DepartmentIn
        default_response_body = DepartmentOut

        list_departments = views.ListView()
        create_department = views.CreateView()
        read_department = views.ReadView()
        update_department = views.UpdateView()
        delete_department = views.DeleteView()


    # If you don't want to use the class attribute approach, you can call the
    # `add_views_to` method manually after the class is defined:
    DepartmentViewSet.add_views_to(router)
    ```
    """

    api: Optional[ninja.NinjaAPI] = None
    router: Optional[ninja.Router] = None
    model: Optional[Type[django.db.models.Model]] = None
    default_request_body: Optional[Type[pydantic.BaseModel]] = None
    default_response_body: Optional[Type[Any]] = None

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        if hasattr(cls, "api") and cls.api is not None:
            cls.add_views_to(cls.api)
        elif hasattr(cls, "router") and cls.router is not None:
            cls.add_views_to(cls.router)

    @classmethod
    def add_views_to(cls, api_or_router: Union[ninja.NinjaAPI, ninja.Router]) -> None:
        """
        Automatically registers all API views defined as class attributes with the
        provided `NinjaAPI` or `Router` instance.

        This method iterates over all class attributes and registers any that are
        instances of `APIView` with the provided `NinjaAPI` or `Router` instance, by
        calling the `add_view_to` method on each view.
        """
        view_members = {
            name: member
            for name, member in inspect.getmembers(cls)
            if isinstance(member, views.APIView)
        }

        ordered_view_members = sorted(
            view_members.items(),
            key=lambda view_member: list(cls.__dict__).index(view_member[0]),
        )
        for name, api_view in ordered_view_members:
            if api_view.view_function_name is None:
                api_view.view_function_name = name
            api_view.set_api_viewset_class(cls)
            api_view.add_view_to(api_or_router)
