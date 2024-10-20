from types import FunctionType
from typing import Annotated, Any, Callable, Optional, Union, cast

from django.db.models import ManyToManyField, Model
from django.http import HttpRequest
from ninja.params.functions import Body, Path
from pydantic import BaseModel

from ninja_crud.views.api_view import APIView
from ninja_crud.views.types import Decorator, ModelGetter, ModelHook


class CreateView(APIView):
    """
    Declarative class-based view for creating a model instance in Django Ninja.

    This class provides a standard implementation for a create view, which creates a
    new model instance based on the request body and saves it to the database. It is
    intended to be used in viewsets or as standalone views to simplify the creation of
    create endpoints.

    Args:
        name (str | None, optional): View function name. Defaults to `None`. If None,
            uses class attribute name in viewsets or "handler" for standalone views.
        methods (list[str] | set[str], optional): HTTP methods. Defaults to `["POST"]`.
        path (str, optional): URL path. Defaults to `"/{id}"`.
        response_status (int, optional): HTTP response status code. Defaults to `201`.
        response_body (Any, optional): Response body type. Defaults to `None`.
            If None, uses the default response body of the viewset.
        model (type[django.db.models.Model], optional): Associated Django model.
            Inherits from viewset if not provided. Defaults to `None`.
        path_parameters (type[BaseModel], optional): Path parameters type.
            Defaults to `None`. If not provided, resolved from the path and model.
        request_body (Any, optional): The request body type. Defaults to `None`.
            If None, uses the default request body of the viewset.
        init_model ((HttpRequest, BaseModel | None) -> Model, optional): Initializes
            the model instance. Default creates a new instance of the model with no
            arguments: `lambda request, path_parameters: self.model()`.
            Useful for customizing model initialization logic, e.g., setting default
            values, using request's user, using path parameters, etc.
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
        create_department = views.CreateView()

        # Usage with explicit request and response bodies:
        create_department = views.CreateView(
            request_body=DepartmentIn,
            response_body=DepartmentOut,
        )

    # Usage as a standalone view:
    views.CreateView(
        name="create_department",
        model=Department,
        request_body=DepartmentIn,
        response_body=DepartmentOut,
    ).add_view_to(api)
    ```
    """

    def __init__(
        self,
        name: Optional[str] = None,
        methods: Union[list[str], set[str], None] = None,
        path: str = "/",
        response_status: int = 201,
        response_body: Any = None,
        model: Optional[type[Model]] = None,
        path_parameters: Optional[type[BaseModel]] = None,
        request_body: Optional[type[BaseModel]] = None,
        init_model: Optional[ModelGetter] = None,
        pre_save: Optional[ModelHook] = None,
        post_save: Optional[ModelHook] = None,
        decorators: Optional[list[Decorator]] = None,
        operation_kwargs: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            name=name,
            methods=methods or ["POST"],
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
        self.init_model = init_model or self._default_init_model
        self.pre_save = pre_save or (lambda request, instance: instance.full_clean())
        self.post_save = post_save or (lambda request, instance: None)

    def handler(
        self,
        request: HttpRequest,
        path_parameters: Optional[BaseModel],
        request_body: BaseModel,
    ) -> Model:
        instance = self.init_model(request, path_parameters)

        m2m_fields_to_set = []
        for field, value in request_body.model_dump().items():
            if isinstance(instance._meta.get_field(field), ManyToManyField):
                m2m_fields_to_set.append((field, value))
            else:
                setattr(instance, field, value)

        self.pre_save(request, instance)
        instance.save()
        self.post_save(request, instance)

        for field, value in m2m_fields_to_set:
            getattr(instance, field).set(value)

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

    def _default_init_model(
        self, request: HttpRequest, path_parameters: Optional[BaseModel]
    ) -> Model:
        return cast(type[Model], self.model)()

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
