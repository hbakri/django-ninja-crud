import functools
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Type, Union

import django.db.models
import django.http
import ninja
import pydantic

from ninja_crud.views.helpers import PathParametersTypeResolver

if TYPE_CHECKING:  # pragma: no cover
    from ninja_crud.viewsets import APIViewSet

ViewFunction = Callable[
    [
        django.http.HttpRequest,
        Optional[pydantic.BaseModel],
        Optional[pydantic.BaseModel],
        Optional[pydantic.BaseModel],
    ],
    Any,
]
ViewDecorator = Callable[[Callable[..., Any]], Callable[..., Any]]


class APIView:
    """
    Base class for creating declarative and reusable API views like components.

    This class provides a framework for defining API views with a declarative syntax
    and minimal boilerplate code. It handles setting up the HTTP method, path, response
    status, and request/response bodies, among other configurations.

    This class is intended to be subclassed, not used directly, although it can be.
    By subclassing, you can create custom API views that leverage the provided
    functionality, enabling you to refactor common view logic into reusable components.

    Args:
        method (str): The HTTP method for the view.
        path (str): The URL path for the view.
        response_status (int): The HTTP status code for the response.
        response_body (Optional[Type[Any]]): The response body type.
        view_function (ViewFunction): The function that handles the view logic.
            Should have the signature:
            - `view_function(request: HttpRequest, path_parameters: Optional[BaseModel],
            query_parameters: Optional[BaseModel], request_body: Optional[BaseModel])
            -> Any`.
        view_function_name (Optional[str], optional): The name of the view function.
        path_parameters (Optional[Type[pydantic.BaseModel]], optional): The path
            parameters type. If not provided, it will be resolved automatically based
            on the path and model (see `PathParametersTypeResolver` for more details).
        query_parameters (Optional[Type[pydantic.BaseModel]], optional): The query
            parameters type.
        request_body (Optional[Type[pydantic.BaseModel]], optional): The request body
            type.
        model (Optional[Type[django.db.models.Model]], optional): The model associated
            with the view. If not provided and the view is bound to a `APIViewSet`,
            the model of the viewset will be used.
        decorators (Optional[List[ViewDecorator]], optional): List of decorators to
            apply to the view function. Decorators are applied in reverse order.
        operation_kwargs (Optional[Dict[str, Any]], optional): Additional keyword
            arguments for the operation.

    Examples:

    Thanks to the flexibility of `APIView`, you can create a wide variety of views
    with minimal boilerplate code. Here is an example of how you can create a simple
    reusable read view by subclassing `APIView`:
    ```python
    # examples/reusable_views.py
    from typing import Optional, Type
    import pydantic
    import django.http
    from django.db import models
    from ninja_crud.views import APIView

    class ReusableReadView(APIView):
        def __init__(
            self,
            model: Optional[Type[models.Model]] = None,
            response_body: Optional[Type[pydantic.BaseModel]] = None,
        ) -> None:
            super().__init__(
                method="GET",
                path="/custom-path/{id}",
                response_status=200,
                response_body=response_body,
                view_function=self._view_function,
                model=model,
            )

        def _view_function(
            self,
            request: django.http.HttpRequest,
            path_parameters: Optional[pydantic.BaseModel],
            query_parameters: Optional[pydantic.BaseModel],
            request_body: Optional[pydantic.BaseModel],
        ) -> models.Model:
            return self.model.objects.get(id=path_parameters.id)
    ```

    You can then directly use the view but first, let's create a simple django model:
    ```python
    # examples/models.py
    import uuid
    from django.db import models

    class Department(models.Model):
        id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
        title = models.CharField(max_length=100, unique=True)
    ```

    Next, we need of course a `ninja.Schema` for serializing the response body:
    ```python
    # examples/schemas.py
    from uuid import UUID
    import ninja

    class DepartmentOut(ninja.Schema):
        id: UUID
        name: str
    ```

    Now, we can declaratively create an endpoint using the `ReusableReadView` class
    we defined earlier in order to read a model instance:
    ```python
    # examples/views.py
    from ninja import NinjaAPI, Router

    from examples.models import Department
    from examples.schemas import DepartmentOut
    from examples.reusable_views import ReusableReadView

    api = NinjaAPI()

    ReusableReadView(model=Department, response_body=DepartmentOut).add_view_to(api)

    # or `add_view_to` can be called with a router instance
    router = Router()

    ReusableReadView(model=Department, response_body=DepartmentOut).add_view_to(router)
    ```

    Or, you can create a viewset in order to group related views together:
    ```python
    # examples/views.py
    from ninja import NinjaAPI
    from ninja_crud.viewsets import APIViewSet

    from examples.models import Department
    from examples.schemas import DepartmentOut
    from examples.reusable_views import ReusableReadView

    api = NinjaAPI()

    class DepartmentViewSet(APIViewSet):
        api = api
        model = Department
        read_department = ReusableReadView(response_body=DepartmentOut)
    ```

    And then, you can add api in the urls.py:
    ```python
    # examples/urls.py
    from django.urls import path

    from examples.views import api as department_api

    urlpatterns = [
        path("departments/", department_api.urls),
    ]
    ```
    """

    def __init__(
        self,
        method: str,
        path: str,
        response_status: int,
        response_body: Optional[Type[Any]],
        view_function: ViewFunction,
        view_function_name: Optional[str] = None,
        path_parameters: Optional[Type[pydantic.BaseModel]] = None,
        query_parameters: Optional[Type[pydantic.BaseModel]] = None,
        request_body: Optional[Type[pydantic.BaseModel]] = None,
        model: Optional[Type[django.db.models.Model]] = None,
        decorators: Optional[List[ViewDecorator]] = None,
        operation_kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.method = method
        self.path = path
        self.response_status = response_status
        self.response_body = response_body
        self.view_function = view_function
        self.view_function_name = view_function_name
        self.path_parameters = path_parameters
        self.query_parameters = query_parameters
        self.request_body = request_body
        self.decorators = decorators or []
        self.model = model
        self.operation_kwargs = operation_kwargs or {}
        self._api_viewset_class: Optional[Type["APIViewSet"]] = None

        if self.path_parameters is None:
            self._resolve_path_parameters_type()

    def add_view_to(self, api_or_router: Union[ninja.NinjaAPI, ninja.Router]) -> None:
        """
        Add the view to an API or router. This method is here for convenience and
        allows you to add the view to an API or router without having to manually
        convert the view to an API operation dictionary (see `as_operation`).

        Args:
            api_or_router (Union[ninja.NinjaAPI, ninja.Router]): The API or router to
                add the view to.

        Example:
        ```python
        from ninja import Router

        from examples.models import Department
        from examples.schemas import DepartmentOut
        from examples.reusable_views import ReusableReadView

        router = Router()

        ReusableReadView(Department, DepartmentOut).add_view_to(router)
        ```
        """
        if isinstance(api_or_router, ninja.NinjaAPI):
            router = api_or_router.default_router
        else:
            router = api_or_router

        router.add_api_operation(**self.as_operation())

    def as_operation(self) -> Dict[str, Any]:
        """
        Return a dictionary representation of the API operation that can be added to a
        router or API by using `add_api_operation` method. Used internally by
        `add_view_to`, but can also be called manually to add the view to a router.

        Returns:
            Dict[str, Any]: The API operation dictionary.

        Example:
        ```python
        from ninja import Router

        from examples.models import Department
        from examples.schemas import DepartmentOut
        from examples.reusable_views import ReusableReadView

        router = Router()

        read_department = ReusableReadView(Department, DepartmentOut)
        router.add_api_operation(**read_department.as_operation())
        ```
        """
        return {
            "path": self.path,
            "methods": [self.method],
            "view_func": self.view_func,
            "response": {self.response_status: self.response_body},
            **self.operation_kwargs,
        }

    @functools.cached_property
    def view_func(self) -> ViewFunction:
        """
        Return the wrapped view function with path, query, and request body parameters
        annotated, and any decorators applied.

        Returns:
            ViewFunction: The wrapped view function.
        """

        def wrapped_view_function(
            request: django.http.HttpRequest,
            path_parameters: Any = ninja.Path(default=None, include_in_schema=False),
            query_parameters: Any = ninja.Query(default=None, include_in_schema=False),
            request_body: Any = ninja.Body(default=None, include_in_schema=False),
        ) -> Any:
            return self.view_function(
                request, path_parameters, query_parameters, request_body
            )

        wrapped_view_function.__annotations__.update(
            {
                "path_parameters": self.path_parameters,
                "query_parameters": self.query_parameters,
                "request_body": self.request_body,
            }
        )
        if self.view_function_name is not None:
            wrapped_view_function.__name__ = self.view_function_name

        for decorator in reversed(self.decorators):
            wrapped_view_function = decorator(wrapped_view_function)

        return wrapped_view_function

    def get_api_viewset_class(self) -> Type["APIViewSet"]:
        """
        Get the viewset class that the view is associated with, if the view is of
        course bound to a viewset class.

        Returns:
            Type[APIViewSet]: The viewset class.

        Raises:
            ValueError: If the view is not bound to a viewset class.
        """
        if self._api_viewset_class is None:
            raise ValueError(
                f"Viewset class not bound to {self.__class__.__name__}. "
                "Please bind a viewset class before calling this method."
            )
        return self._api_viewset_class

    def set_api_viewset_class(self, api_viewset_class: Type["APIViewSet"]) -> None:
        """
        Bind the view to a viewset class. This method sets the model and path
        parameters type based on the viewset class. Can be overridden in subclasses
        to provide additional behavior, like setting default values for the view.

        Args:
            api_viewset_class (Type[APIViewSet]): The viewset class to bind to.

        Raises:
            ValueError: If the view is already bound to a viewset class.

        Note:
            This method is called internally and automatically by the viewset when
            defining views as class attributes. It should not be called manually.
        """
        if self._api_viewset_class is not None:
            raise ValueError(
                f"{self.__class__.__name__} is already bound to a viewset class."
            )
        self._api_viewset_class = api_viewset_class

        if self.model is None:
            self.model = api_viewset_class.model

        if self.path_parameters is None:
            self._resolve_path_parameters_type()

    def _resolve_path_parameters_type(self) -> None:
        if self.model is not None:
            self.path_parameters = PathParametersTypeResolver.resolve(
                path=self.path, model_class=self.model
            )
