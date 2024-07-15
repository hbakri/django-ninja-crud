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

from django.db.models import ManyToManyField, Model
from django.http import HttpRequest
from ninja.params.functions import Body, Path
from pydantic import BaseModel
from typing_extensions import Annotated

from ninja_crud.views.api_view import APIView

if TYPE_CHECKING:  # pragma: no cover
    from ninja_crud.viewsets import APIViewSet


class UpdateView(APIView):
    """
    Declarative class-based view for updating a model instance in Django Ninja.

    This class provides a standard implementation for an update view, which retrieves
    a single model instance based on the path parameters, updates the instance based on
    the request body, and saves the changes to the database. It is intended to be used
    in viewsets or as standalone views to simplify the creation of update endpoints.

    Args:
        name (str | None, optional): View function name. Defaults to `None`.
            If None, uses class attribute name in viewsets or "handler" for standalone
            views (unless decorator-overridden).
        method (str, optional): The HTTP method for the view. Defaults to `"PUT"`.
        path (str, optional): The URL path for the view. Defaults to `"/{id}"`.
        response_status (int, optional): HTTP response status code. Defaults to `200`.
        response_body (Type | None, optional): Response body type. Defaults to `None`.
            If None, uses the default response body of the viewset.
        model (Type[django.db.models.Model] | None, optional): Associated Django model.
            Inherits from viewset if not provided. Defaults to `None`.
        path_parameters (Type[BaseModel] | None, optional): Path parameters type.
            Defaults to `None`. If not provided, resolved from the path and model.
        request_body (Type[BaseModel] | None, optional): The request body type.
            Defaults to `None`. If None, uses the default request body of the viewset.
        get_model (Callable | None, optional): Retrieves model instance. Default uses
            path parameters (e.g., `self.model.objects.get(id=path_parameters.id)`
            for `/{id}` path). Useful for customizing model retrieval logic.
            Should have the signature:
            - `(request: HttpRequest, path_parameters: Optional[BaseModel]) -> Model`
        pre_save (Callable | None, optional): Pre-save operations on the model instance.
            Default calls `full_clean` on the instance. Should have the signature:
            - `(request: HttpRequest, instance: Model) -> None`
        post_save (Callable | None, optional): Post-save operations on the model instance.
            Default does nothing. Should have the signature:
            - `(request: HttpRequest, instance: Model) -> None`
        decorators (List[Callable] | None, optional): View function decorators
            (applied in reverse order). Defaults to `None`.
        operation_kwargs (Dict[str, Any] | None, optional): Additional operation
            keyword arguments. Defaults to `None`.

    Example:
    ```python
    from ninja import NinjaAPI
    from ninja_crud import views, viewsets

    from examples.models import Department
    from examples.schemas import DepartmentIn, DepartmentOut

    api = NinjaAPI()

    # Usage as a class attribute in a viewset:
    class DepartmentViewSet(viewsets.APIViewSet):
        api = api
        model = Department
        default_request_body = DepartmentIn
        default_response_body = DepartmentOut

        # Usage with default request and response bodies:
        update_department = views.UpdateView()

        # Usage with explicit request and response bodies:
        update_department = views.UpdateView(
            request_body=DepartmentIn,
            response_body=DepartmentOut,
        )

    # Usage as a standalone view:
    views.UpdateView(
        name="update_department",
        model=Department,
        request_body=DepartmentIn,
        response_body=DepartmentOut,
    ).add_view_to(api)
    ```
    """

    def __init__(
        self,
        name: Optional[str] = None,
        method: str = "PUT",
        path: str = "/{id}",
        response_status: int = 200,
        response_body: Optional[Type[Any]] = None,
        model: Optional[Type[Model]] = None,
        path_parameters: Optional[Type[BaseModel]] = None,
        request_body: Optional[Type[BaseModel]] = None,
        get_model: Optional[Callable[[HttpRequest, Optional[BaseModel]], Model]] = None,
        pre_save: Optional[Callable[[HttpRequest, Model], None]] = None,
        post_save: Optional[Callable[[HttpRequest, Model], None]] = None,
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
        self.request_body = request_body
        self.get_model = get_model or self._default_get_model
        self.pre_save = pre_save or self._default_pre_save
        self.post_save = post_save or self._default_post_save

    def handler(
        self,
        request: HttpRequest,
        path_parameters: Optional[BaseModel],
        request_body: BaseModel,
    ) -> Model:
        instance = self.get_model(request, path_parameters)

        for field, value in request_body.model_dump(exclude_unset=True).items():
            if isinstance(instance._meta.get_field(field), ManyToManyField):
                getattr(instance, field).set(value)
            else:
                setattr(instance, field, value)

        self.pre_save(request, instance)
        instance.save()
        self.post_save(request, instance)
        return instance

    def _update_handler_annotations(
        self, handler: Callable[..., Any]
    ) -> Callable[..., Any]:
        annotations = cast(FunctionType, handler).__annotations__
        annotations["path_parameters"] = Annotated[
            self.path_parameters, Path(default=None, include_in_schema=False)
        ]
        annotations["request_body"] = Annotated[self.request_body, Body()]
        return handler

    def _default_get_model(
        self, request: HttpRequest, path_parameters: Optional[BaseModel]
    ) -> Model:
        if self.model is None:
            raise ValueError("No model set for the view.")

        return self.model.objects.get(
            **(path_parameters.dict() if path_parameters else {})
        )

    @staticmethod
    def _default_pre_save(request: HttpRequest, instance: Model) -> None:
        instance.full_clean()

    @staticmethod
    def _default_post_save(request: HttpRequest, instance: Model) -> None:
        pass

    def set_api_viewset_class(self, api_viewset_class: Type["APIViewSet"]) -> None:
        """
        Bind the view to a viewset class.

        This method sets the model and path parameters type based on the viewset class,
        and assigns the request body and response body from the viewset class's
        `default_request_body` and `default_response_body`, respectively, if they are
        not already set.

        Note:
            This method is called internally and automatically by the viewset when
            defining views as class attributes. It should not be called manually.
        """
        super().set_api_viewset_class(api_viewset_class)
        self.path_parameters = self.path_parameters or self.resolve_path_parameters()
        self.request_body = self.request_body or api_viewset_class.default_request_body
        self.response_body = (
            self.response_body or api_viewset_class.default_response_body
        )
