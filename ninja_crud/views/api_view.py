import abc
import functools
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Type, Union

import django.db.models
import ninja
import ninja.orm.fields
import ninja.signature.utils
import pydantic

if TYPE_CHECKING:  # pragma: no cover
    from ninja_crud.viewsets import APIViewSet


class APIView(abc.ABC):
    """
    Base class for creating declarative and reusable API views like components.

    This class provides a framework for defining API views with a declarative syntax
    and minimal boilerplate code. It handles setting up the HTTP methods, path, response
    status/body, among other configurations.

    This class is intended to be subclassed, not used directly.
    By subclassing, you can create custom API views that leverage the provided
    functionality, enabling you to refactor common view logic into reusable components.

    Args:
        name (str | None): View function name. If None, uses class attribute name in
            viewsets or "handler" for standalone views (unless decorator-overridden).
        methods (List[str]): HTTP methods.
        path (str): URL path.
        response_status (int): HTTP response status code.
        response_body (Type | None): Response body type.
        model (Type[django.db.models.Model] | None, optional): Associated Django model.
            Inherits from viewset if not provided. Defaults to `None`.
        decorators (List[Callable] | None, optional): View function decorators
            (applied in reverse order). Defaults to `None`.
        operation_kwargs (Dict[str, Any] | None, optional): Additional operation
            keyword arguments. Defaults to `None`.

    Examples:

    Thanks to the flexibility of `APIView`, you can create a wide variety of views
    with minimal boilerplate code. Here is an example of how you can create a simple
    reusable read view supporting only models with a UUID primary key:
    ```python
    # examples/reusable_views.py
    from uuid import UUID
    from typing import Optional, Type
    from pydantic import BaseModel
    from django.http import HttpRequest
    from django.db import models
    from ninja_crud.views import APIView

    class ReusableReadView(APIView):
        def __init__(
            self,
            name: Optional[str] = None,
            model: Optional[Type[models.Model]] = None,
            response_body: Optional[Type[BaseModel]] = None,
        ) -> None:
            super().__init__(
                name=name,
                methods=["GET"],
                path="/{id}/reusable",
                response_status=200,
                response_body=response_body,
                model=model,
            )

        def handler(self, request: HttpRequest, id: UUID) -> models.Model:
            return self.model.objects.get(id=id)
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

    ReusableReadView(
        name="read_department",
        model=Department,
        response_body=DepartmentOut
    ).add_view_to(api)

    # or `add_view_to` can be called with a router instance
    router = Router()

    ReusableReadView(
        name="read_department",
        model=Department,
        response_body=DepartmentOut
    ).add_view_to(router)
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
        name: Optional[str],
        methods: List[str],
        path: str,
        response_status: int,
        response_body: Optional[Type[Any]],
        model: Optional[Type[django.db.models.Model]] = None,
        decorators: Optional[
            List[Callable[[Callable[..., Any]], Callable[..., Any]]]
        ] = None,
        operation_kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.name = name
        self.methods = methods
        self.path = path
        self.response_status = response_status
        self.response_body = response_body
        self.model = model
        self.decorators = decorators or []
        self.operation_kwargs = operation_kwargs or {}
        self._api_viewset_class: Optional[Type[APIViewSet]] = None

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
            "methods": self.methods,
            "view_func": functools.reduce(
                lambda f, g: g(f),
                reversed(self.decorators),
                self.wrap_handler(self.handler),
            ),
            "response": {self.response_status: self.response_body},
            **self.operation_kwargs,
        }

    @abc.abstractmethod
    def handler(self, *args: Any, **kwargs: Any) -> Any:
        """
        The handler function for the view. This method must be implemented in
        subclasses and should contain the view's business logic.

        Args:
            *args (Any): Variable positional arguments.
            **kwargs (Any): Variable keyword arguments.

        Returns:
            Any: The response data.
        """

    def wrap_handler(self, handler: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(handler)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return handler(*args, **kwargs)

        if self.name is not None:
            wrapper.__name__ = self.name

        return wrapper

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
        Bind the view to a viewset class. This method sets the model based on the
        viewset class if not already defined. Can be overridden in subclasses to
        provide additional behavior, like setting default values for the view.

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

    def resolve_path_parameters(self) -> Optional[Type[pydantic.BaseModel]]:
        """
        Resolve path parameters to a pydantic model based on the view's path and model.

        Designed for subclasses, this method enables dynamic path parameter handling
        without explicit type specification. It supports any paths, like "/{name}",
        "/{id}", or "/{related_model_id}", automatically resolving types from model
        fields.

        This feature *significantly* reduces boilerplate code and allows for easy
        creation of reusable views with varied path structures, especially useful when
        refactoring repetitive endpoints into an APIView subclass.

        Utilizes Django Ninja utilities to extract and map path parameters to model
        fields. Returns `None` if no parameters are found.

        Returns:
            Optional[Type[pydantic.BaseModel]]: Path parameters pydantic model type.

        Example:
            For path `"/{department_id}/employees/{id}"` and `Employee` model:

            ```python
            class PathParameters(pydantic.BaseModel):
                department_id: UUID
                id: UUID
            ```

        Notes:
            - Supports various Django field types (e.g., AutoField, CharField,
                DateField, UUIDField).
            - For ForeignKey, uses the primary key type of the related model.
            - Supports both real field names (e.g., /{department_id}) and related
                model names (e.g., /{department}).

        Important:
            Prefer simple types (strings, integers, UUIDs) for path parameters to
            ensure proper URL formatting and web standard compatibility.
        """
        if self.model is None:
            return None

        path_parameters_names = ninja.signature.utils.get_path_param_names(self.path)
        if not path_parameters_names:
            return None

        field_definitions: Dict[str, Any] = {
            path_parameter_name: ninja.orm.fields.get_schema_field(
                field=self.model._meta.get_field(field_name=path_parameter_name),
            )
            for path_parameter_name in path_parameters_names
        }
        return pydantic.create_model("PathParameters", **field_definitions)
