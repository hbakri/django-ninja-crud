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

if TYPE_CHECKING:
    from ninja_crud.viewsets import APIViewSet


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
        methods (List[str], optional): HTTP methods. Defaults to `["POST"]`.
        path (str, optional): URL path. Defaults to `"/"`.
        response_status (int, optional): HTTP response status code. Defaults to `201`.
        response_body (Type | None, optional): Response body type. Defaults to `None`.
            If None, uses the default response body of the viewset.
        model (Type[django.db.models.Model] | None, optional): Associated Django model.
            Inherits from viewset if not provided. Defaults to `None`.
        path_parameters (Type[BaseModel] | None, optional): Path parameters type.
            Defaults to `None`. If not provided, resolved from the path and model.
        request_body (Type[BaseModel] | None, optional): The request body type.
            Defaults to `None`. If None, uses the default request body of the viewset.
        init_model (Callable | None, optional): Initialize the model instance.
            Default uses `self.model()`. Should have the signature:
            - `(request: HttpRequest, path_parameters: Optional[BaseModel]) -> Model`
        pre_save (Callable | None, optional): Pre-create operations on the model instance.
            Default calls `full_clean` on the instance. Should have the signature:
            - `(request: HttpRequest, instance: Model) -> None`
        post_save (Callable | None, optional): Post-create operations on the model instance.
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
        methods: Optional[List[str]] = None,
        path: str = "/",
        response_status: int = 201,
        response_body: Optional[Type[Any]] = None,
        model: Optional[Type[Model]] = None,
        path_parameters: Optional[Type[BaseModel]] = None,
        request_body: Optional[Type[BaseModel]] = None,
        init_model: Optional[
            Callable[[HttpRequest, Optional[BaseModel]], Model]
        ] = None,
        pre_save: Optional[Callable[[HttpRequest, Model], None]] = None,
        post_save: Optional[Callable[[HttpRequest, Model], None]] = None,
        decorators: Optional[
            List[Callable[[Callable[..., Any]], Callable[..., Any]]]
        ] = None,
        operation_kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            name=name,
            methods=methods or ["POST"],
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
        self.init_model = init_model or self._default_init_model
        self.pre_save = pre_save or self._default_pre_save
        self.post_save = post_save or self._default_post_save

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
        if self.model is None:
            raise ValueError("No model set for the view.")

        return self.model()

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
