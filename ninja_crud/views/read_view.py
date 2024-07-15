from types import FunctionType
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Type,
    cast,
)

from django.db.models import Model
from django.http import HttpRequest
from ninja.params.functions import Path
from pydantic import BaseModel
from typing_extensions import Annotated

from ninja_crud.views.api_view import APIView

if TYPE_CHECKING:  # pragma: no cover
    from ninja_crud.viewsets import APIViewSet


class ReadView(APIView):
    """
    Declarative class-based view for reading a model instance in Django Ninja.

    This class provides a standard implementation for a read view, which retrieves
    a single model instance based on the path parameters. It is intended to be used
    in viewsets or as standalone views to simplify the creation of read endpoints.

    Args:
        name (str | None, optional): View function name. Defaults to `None`.
            If None, uses class attribute name in viewsets or "handler" for standalone
            views (unless decorator-overridden).
        method (str, optional): The HTTP method for the view. Defaults to `"GET"`.
        path (str, optional): The URL path for the view. Defaults to `"/{id}"`.
        response_status (int, optional): HTTP response status code. Defaults to `200`.
        response_body (Type | None, optional): Response body type. Defaults to `None`.
            If None, uses the default response body of the viewset.
        path_parameters (Type[BaseModel] | None, optional): Path parameters type.
            Defaults to `None`. If not provided, resolved from the path and model.
        model (Type[django.db.models.Model] | None, optional): Associated Django model.
            Inherits from viewset if not provided. Defaults to `None`.
        get_model (Callable | None, optional): Retrieves model instance. Default uses
            path parameters (e.g., `self.model.objects.get(id=path_parameters.id)`
            for `/{id}` path). Useful for customizing model retrieval logic.
            Should have the signature:
            - `(request: HttpRequest, path_parameters: Optional[BaseModel]) -> Model`
        decorators (List[Callable] | None, optional): View function decorators
            (applied in reverse order). Defaults to `None`.
        operation_kwargs (Dict[str, Any] | None, optional): Additional operation
            keyword arguments. Defaults to `None`.

    Example:
    ```python
    from ninja import NinjaAPI
    from ninja_crud import views, viewsets

    from examples.models import Department
    from examples.schemas import DepartmentOut

    api = NinjaAPI()

    # Usage as a class attribute in a viewset:
    class DepartmentViewSet(viewsets.APIViewSet):
        api = api
        model = Department
        default_response_body = DepartmentOut

        # Usage with default response body:
        read_department = views.ReadView()

        # Usage with explicit response body:
        read_department = views.ReadView(response_body=DepartmentOut)

    # Usage as a standalone view:
    views.ReadView(
        name="read_department",
        model=Department,
        response_body=DepartmentOut,
    ).add_view_to(api)
    ```
    """

    def __init__(
        self,
        name: Optional[str] = None,
        method: str = "GET",
        path: str = "/{id}",
        response_status: int = 200,
        response_body: Optional[Type[Any]] = None,
        model: Optional[Type[Model]] = None,
        path_parameters: Optional[Type[BaseModel]] = None,
        get_model: Optional[Callable[[HttpRequest, Optional[BaseModel]], Model]] = None,
        decorators: Optional[
            List[Callable[[Callable[..., Any]], Callable[..., Any]]]
        ] = None,
        operation_kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            name=name,
            method=method,
            path=path,
            response_status=response_status,
            response_body=response_body,
            model=model,
            decorators=decorators,
            operation_kwargs=operation_kwargs,
        )
        self.decorators.append(self._update_handler_annotations)
        self.path_parameters = path_parameters or self.resolve_path_parameters()
        self.get_model = get_model or self._default_get_model

    def handler(
        self,
        request: HttpRequest,
        path_parameters: Optional[BaseModel],
    ) -> Model:
        return self.get_model(request, path_parameters)

    def _update_handler_annotations(
        self, handler: Callable[..., Any]
    ) -> Callable[..., Any]:
        annotations = cast(FunctionType, handler).__annotations__
        annotations["path_parameters"] = Annotated[
            self.path_parameters, Path(default=None, include_in_schema=False)
        ]
        return handler

    def _default_get_model(
        self, request: HttpRequest, path_parameters: Optional[BaseModel]
    ) -> Model:
        if self.model is None:
            raise ValueError("No model set for the view.")

        return self.model.objects.get(
            **(path_parameters.dict() if path_parameters else {})
        )

    def set_api_viewset_class(self, api_viewset_class: Type["APIViewSet"]) -> None:
        """
        Bind the view to a viewset class.

        This method sets the model and path parameters type based on the viewset class,
        and assigns the response body from the viewset class's `default_response_body`
        if the response body is not already set.

        Note:
            This method is called internally and automatically by the viewset when
            defining views as class attributes. It should not be called manually.
        """
        super().set_api_viewset_class(api_viewset_class)
        self.path_parameters = self.path_parameters or self.resolve_path_parameters()
        self.response_body = (
            self.response_body or api_viewset_class.default_response_body
        )
