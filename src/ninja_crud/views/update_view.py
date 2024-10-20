from types import FunctionType
from typing import Annotated, Any, Callable, cast

from django.db.models import ManyToManyField, Model
from django.http import HttpRequest
from ninja.params.functions import Body, Path
from pydantic import BaseModel

from ninja_crud.views.api_view import APIView
from ninja_crud.views.types import Decorator, ModelGetter, ModelHook


class UpdateView(APIView):
    """
    Declarative class-based view for updating a model instance in Django Ninja.

    This class provides a standard implementation for an update view, which retrieves
    a single model instance based on the path parameters, updates the instance based on
    the request body, and saves the changes to the database. It is intended to be used
    in viewsets or as standalone views to simplify the creation of update endpoints.

    Args:
        name (str | None, optional): View function name. Defaults to `None`. If None,
            uses class attribute name in viewsets or "handler" for standalone views.
        methods (list[str] | set[str], optional): HTTP methods. Defaults to `["PUT"]`.
        path (str, optional): URL path. Defaults to `"/{id}"`.
        response_status (int, optional): HTTP response status code. Defaults to `200`.
        response_body (Any, optional): Response body type. Defaults to `None`.
            If None, uses the default response body of the viewset.
        model (type[django.db.models.Model], optional): Associated Django model.
            Inherits from viewset if not provided. Defaults to `None`.
        path_parameters (type[BaseModel], optional): Path parameters type.
            Defaults to `None`. If not provided, resolved from the path and model.
        request_body (Any, optional): The request body type. Defaults to `None`.
            If None, uses the default request body of the viewset.
        get_model ((HttpRequest, BaseModel | None) -> Model, optional): Retrieves model
            instance. Default uses path parameters (e.g., `self.model.objects.get(id=path_parameters.id)`
            for `/{id}` path). Useful for customizing model retrieval logic.
            Should have the signature:
            - `(request: HttpRequest, path_parameters: BaseModel | None) -> Model`
        pre_save ((HttpRequest, Model) -> None, optional): Pre-save operations on the
            model instance. Does a [full_clean](https://docs.djangoproject.com/en/stable/ref/models/instances/#django.db.models.Model.full_clean)
            by default.
        post_save ((HttpRequest, Model) -> None, optional): Post-save operations on the
            model instance. Does nothing by default.
        decorators (list[Callable], optional): View function decorators
            (applied in reverse order). Defaults to `None`.
        operation_kwargs (dict[str, Any], optional): Additional operation
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
        name: str | None = None,
        methods: list[str] | set[str] | None = None,
        path: str = "/{id}",
        response_status: int = 200,
        response_body: Any = None,
        model: type[Model] | None = None,
        path_parameters: type[BaseModel] | None = None,
        request_body: type[BaseModel] | None = None,
        get_model: ModelGetter | None = None,
        pre_save: ModelHook | None = None,
        post_save: ModelHook | None = None,
        decorators: list[Decorator] | None = None,
        operation_kwargs: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            name=name,
            methods=methods or ["PUT"],
            path=path,
            status_code=response_status,
            response_schema=response_body,
            decorators=decorators,
            operation_kwargs=operation_kwargs,
        )
        self.model = model
        self.decorators.append(self._update_handler_annotations)
        self.path_parameters = path_parameters
        self.request_body = request_body
        self.get_model = get_model or self._default_get_model
        self.pre_save = pre_save or (lambda request, instance: instance.full_clean())
        self.post_save = post_save or (lambda request, instance: None)

    def handler(
        self,
        request: HttpRequest,
        path_parameters: BaseModel | None,
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
        self, request: HttpRequest, path_parameters: BaseModel | None
    ) -> Model:
        return cast(type[Model], self.model).objects.get(
            **(path_parameters.model_dump() if path_parameters else {})
        )

    def as_operation(self) -> dict[str, Any]:
        if self.api_viewset_class:
            self.model = self.model or self.api_viewset_class.model
            self.request_body = (
                self.request_body or self.api_viewset_class.default_request_body
            )
            self.response_schema = (
                self.response_schema or self.api_viewset_class.default_response_body
            )

        if not self.model:
            raise ValueError(
                f"Unable to determine model for view {self.name}. "
                "Please set a model either on the view or on its associated viewset."
            )
        self.path_parameters = self.path_parameters or self.resolve_path_parameters(
            self.model
        )
        return super().as_operation()
