import abc
import asyncio
import functools
import typing
from typing import TYPE_CHECKING, Any, Callable

import django.db.models
import ninja
import ninja.orm.fields
import ninja.signature.utils
import pydantic
from ninja.constants import NOT_SET

from ninja_crud.views.types import Decorator

if TYPE_CHECKING:
    from ninja_crud.viewsets import APIViewSet


class APIView(abc.ABC):
    """
    Base class for creating declarative and reusable API views like components.

    This class provides a framework for defining API views with a declarative syntax
    and minimal boilerplate code. It handles setting up the HTTP methods, path, response
    status/body, among other configurations. It supports both synchronous and
    asynchronous handlers, allowing for flexible view implementations.

    This class is intended to be subclassed, not used directly.
    By subclassing, you can create custom API views that leverage the provided
    functionality, enabling you to refactor common view logic into reusable components.

    Args:
        path (str): The URL path to be used for this *path operation*. It can contain
            path parameters in the format `{parameter_name}`. For example, `"/{id}"`.
        methods (list[str] | set[str]): The HTTP methods that this view should handle.
            For example, `["GET"]` or `{"GET", "POST"}`. It can also receive StrEnum
            values, such as Python's [`http.HTTPMethod`](https://docs.python.org/3/library/http.html#http.HTTPMethod).
        response_schema (Any, optional): The type to use for the primary response.
            It can be any valid Pydantic field type, including Pydantic models,
            primitive types, or complex structures like `list` or `dict`.
            Defaults to `ninja.constants.NOT_SET`.
        status_code (int | None, optional): The default status code for the primary
            response. Can be an integer or an `IntEnum` (e.g., Python's
            [`http.HTTPStatus`](https://docs.python.org/3/library/http.html#http.HTTPStatus)).
            If not specified, defaults to `200` when a response_schema is provided.
        responses (dict[int, Any] | None, optional): Additional responses that could be
            returned by this *path operation*. The key is the status code, and the value
            is the response schema. These are merged with the primary response.
            Defaults to `None`.
        name (str, optional): The name of the view function, used by the OpenAPI docs.
            If not provided, defaults to the class attribute name if the view is part
            of a viewset. Defaults to `None`.
        decorators (list[Callable], optional): View function decorators
            (applied in reverse order). Defaults to `None`.
        operation_kwargs (dict[str, Any], optional): Additional operation
            keyword arguments. Defaults to `None`.

    Examples:

    Thanks to the flexibility of `APIView`, you can create a wide variety of views
    with minimal boilerplate code. Here are examples of how you can create simple
    reusable read views supporting models with a UUID primary key, in both
    synchronous and asynchronous variants:

    Synchronous:
    ```python
    from typing import Any
    from uuid import UUID

    from django.http import HttpRequest
    from django.db import models
    from ninja.constants import NOT_SET
    from ninja_crud.views import APIView

    class ReadView(APIView):
        def __init__(
            self,
            response_schema: Any = NOT_SET,
            model: type[models.Model] | None = None,
            name: str | None = None,
        ) -> None:
            super().__init__(
                path="/{id}",
                methods=["GET"],
                response_schema=response_schema,
                status_code=200,
                name=name,
            )
            self.model = model

        def handler(self, request: HttpRequest, id: UUID) -> models.Model:
            return self.model.objects.get(id=id)
    ```

    Asynchronous:
    ```python
    class AsyncReadView(APIView):
        def __init__(
            self,
            response_schema: Any = NOT_SET,
            model: type[models.Model] | None = None,
            name: str | None = None,
        ) -> None:
            super().__init__(
                path="/async/{id}",
                methods=["GET"],
                response_schema=response_schema,
                status_code=200,
                name=name,
            )
            self.model = model

        async def handler(self, request: HttpRequest, id: UUID) -> models.Model:
            return await self.model.objects.aget(id=id)
    ```

    You can then use these views with a simple Django `models.Model`:
    ```python
    # examples/models.py
    import uuid
    from django.db import models

    class Department(models.Model):
        id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
        title = models.CharField(max_length=100, unique=True)
    ```

    And a `ninja.Schema` for serializing the response body:
    ```python
    # examples/schemas.py
    from uuid import UUID
    import ninja

    class DepartmentOut(ninja.Schema):
        id: UUID
        name: str
    ```

    Now, you can declaratively create endpoints using these view classes:
    ```python
    # examples/views.py
    from ninja import NinjaAPI

    from examples.models import Department
    from examples.schemas import DepartmentOut
    from examples.reusable_views import ReadView, AsyncReadView

    api = NinjaAPI()

    ReadView(
        name="read_department",
        model=Department,
        response_schema=DepartmentOut
    ).add_view_to(api)

    AsyncReadView(
        name="async_read_department",
        model=Department,
        response_schema=DepartmentOut
    ).add_view_to(api)
    ```

    Or, you can create a viewset to group related views:
    ```python
    # examples/views.py
    from ninja import NinjaAPI
    from ninja_crud.viewsets import APIViewSet

    from examples.models import Department
    from examples.schemas import DepartmentOut
    from examples.reusable_views import ReadView, AsyncReadView

    api = NinjaAPI()

    class DepartmentViewSet(APIViewSet):
        api = api
        model = Department

        read_department = ReadView(response_schema=DepartmentOut)
        async_read_department = AsyncReadView(response_schema=DepartmentOut)
    ```

    This setup provides both synchronous and asynchronous endpoints for reading
    department data, demonstrating the flexibility of the APIView class in handling
    different types of request handlers.
    """

    def __init__(
        self,
        path: str,
        methods: list[str] | set[str],
        *,
        response_schema: Any = NOT_SET,
        status_code: int | None = None,
        responses: dict[int, Any] | None = None,
        name: str | None = None,
        decorators: list[Decorator] | None = None,
        operation_kwargs: dict[str, Any] | None = None,
    ) -> None:
        self.path = path
        self.methods = methods
        self.response_schema = response_schema
        self.status_code = status_code
        self.responses = responses or {}
        self.name = name
        self.decorators = decorators or []
        self.operation_kwargs = operation_kwargs or {}
        self._api_viewset_class: type[APIViewSet] | None = None

    def add_view_to(self, api_or_router: ninja.NinjaAPI | ninja.Router) -> None:
        """
        Add the view to an API or router. This method is here for convenience and
        allows you to add the view to an API or router without having to manually
        convert the view to an API operation dictionary (see `as_operation`).

        Args:
            api_or_router (ninja.NinjaAPI | ninja.Router): The API or router to
                add the view to.

        Example:
        ```python
        from ninja import Router

        from examples.models import Department
        from examples.schemas import DepartmentOut
        from examples.reusable_views import ReadView

        router = Router()

        ReadView(Department, DepartmentOut).add_view_to(router)
        ```
        """
        if isinstance(api_or_router, ninja.NinjaAPI):
            router = api_or_router.default_router
        else:
            router = api_or_router

        router.add_api_operation(**self.as_operation())

    def as_operation(self) -> dict[str, Any]:
        """
        Return a dictionary representation of the API operation that can be added to a
        router or API by using `add_api_operation` method. Used internally by
        `add_view_to`, but can also be called manually to add the view to a router.

        Returns:
            dict[str, Any]: The API operation dictionary.

        Example:
        ```python
        from ninja import Router

        from examples.models import Department
        from examples.schemas import DepartmentOut
        from examples.reusable_views import ReadView

        router = Router()

        read_department = ReadView(Department, DepartmentOut)
        router.add_api_operation(**read_department.as_operation())
        ```
        """
        responses: dict[int, Any] = {}
        if self.response_schema is not NOT_SET:
            responses[self.status_code or 200] = self.response_schema
        elif self.status_code is not None:
            responses[self.status_code] = None

        responses.update(self.responses)
        return {
            "path": self.path,
            "methods": self.methods,
            "view_func": functools.reduce(
                lambda f, g: g(f),
                reversed(self.decorators),
                self.create_standalone_handler(self.handler),
            ),
            "response": responses or NOT_SET,
            **self.operation_kwargs,
        }

    @abc.abstractmethod
    def handler(self, *args: Any, **kwargs: Any) -> Any:
        """
        The handler function for the view. This method must be implemented in
        subclasses and should contain the view's business logic.

        This method can be implemented as either a synchronous or an asynchronous
        function, depending on the needs of the specific view. The APIView class
        will automatically adapt to the chosen implementation.

        For synchronous implementation:
        def handler(self, request: HttpRequest, ...) -> Any:
            # Synchronous logic here

        For asynchronous implementation:
        async def handler(self, request: HttpRequest, ...) -> Any:
            # Asynchronous logic here

        Args:
            *args (Any): Variable positional arguments.
            **kwargs (Any): Variable keyword arguments.

        Returns:
            Any: The response data. This can be a simple value, a model instance,
                 or any other data that can be serialized by Django Ninja.
        """

    def create_standalone_handler(
        self, method: Callable[..., Any]
    ) -> Callable[..., Any]:
        @functools.wraps(method)
        async def async_handler(*args: Any, **kwargs: Any) -> Any:
            return await method(*args, **kwargs)

        @functools.wraps(method)
        def sync_handler(*args: Any, **kwargs: Any) -> Any:
            return method(*args, **kwargs)

        standalone_handler = (
            async_handler if asyncio.iscoroutinefunction(method) else sync_handler
        )

        if self.name is not None:
            standalone_handler.__name__ = self.name

        return standalone_handler

    @property
    def api_viewset_class(self) -> type["APIViewSet"] | None:
        return self._api_viewset_class

    @api_viewset_class.setter
    def api_viewset_class(self, api_viewset_class: type["APIViewSet"]) -> None:
        if self._api_viewset_class:
            raise ValueError(
                f"View '{self.name}' is already bound to a viewset. "
                "Views cannot be reassigned once they are bound."
            )
        self._api_viewset_class = api_viewset_class

    def resolve_path_parameters(
        self, model: type[django.db.models.Model]
    ) -> type[pydantic.BaseModel] | None:
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

        Args:
            model (type[django.db.models.Model] | None): The associated Django model.

        Returns:
            type[pydantic.BaseModel] | None: Path parameters pydantic model type.

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
        path_parameters_names = ninja.signature.utils.get_path_param_names(self.path)
        if not path_parameters_names:
            return None

        schema_fields: dict[str, Any] = {}
        for field_name in path_parameters_names:
            model_field = model._meta.get_field(field_name)
            schema_field = ninja.orm.fields.get_schema_field(field=model_field)[0]
            schema_fields[field_name] = (
                typing.get_args(schema_field)[0]
                if typing.get_origin(schema_field) is typing.Union
                else schema_field,
                ...,
            )

        return pydantic.create_model("PathParameters", **schema_fields)
