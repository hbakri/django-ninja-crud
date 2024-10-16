from types import FunctionType
from typing import Any, Callable, Dict, List, Optional, Type, cast

from django.db.models import Model
from django.http import HttpRequest
from ninja.params.functions import Path
from pydantic import BaseModel
from typing_extensions import Annotated

from ninja_crud.views.api_view import APIView


class DeleteView(APIView):
    """
    Declarative class-based view for deleting a model instance in Django Ninja.

    This class provides a standard implementation for a delete view, which retrieves
    a single model instance based on the path parameters and deletes it. It is
    intended to be used in viewsets or as standalone views to simplify the creation
    of delete endpoints.

    Args:
        name (str | None, optional): View function name. Defaults to `None`. If None,
            uses class attribute name in viewsets or "handler" for standalone views.
        methods (List[str], optional): HTTP methods. Defaults to `["DELETE"]`.
        path (str, optional): URL path. Defaults to `"/{id}"`.
        response_status (int, optional): HTTP response status code. Defaults to `204`.
        response_body (Type | None, optional): Response body type. Defaults to `None`.
        model (Type[django.db.models.Model] | None, optional): Associated Django model.
            Inherits from viewset if not provided. Defaults to `None`.
        path_parameters (Type[BaseModel] | None, optional): Path parameters type.
            Defaults to `None`. If not provided, resolved from the path and model.
        get_model (Callable | None, optional): Retrieves model instance. Default uses
            path parameters (e.g., `self.model.objects.get(id=path_parameters.id)`
            for `/{id}` path). Useful for customizing model retrieval logic.
            Should have the signature:
            - `(request: HttpRequest, path_parameters: Optional[BaseModel]) -> Model`
        pre_delete (Callable | None, optional): A callable to perform pre-delete
            operations on the model instance. By default, it does nothing. Useful for
            additional operations before deleting the instance.
            Should have the signature:
            - `(request: HttpRequest, instance: Model) -> None`
        post_delete (Callable | None, optional): A callable to perform post-delete
            operations on the model instance. By default, it does nothing. Useful for
            additional operations after deleting the instance.
            Should have the signature:
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

    api = NinjaAPI()

    # Usage as a class attribute in a viewset:
    class DepartmentViewSet(viewsets.APIViewSet):
        api = api
        model = Department

        delete_department = views.DeleteView()

    # Usage as a standalone view:
    views.DeleteView(
        name="delete_department",
        model=Department
    ).add_view_to(api)
    ```
    """

    def __init__(
        self,
        name: Optional[str] = None,
        methods: Optional[List[str]] = None,
        path: str = "/{id}",
        response_status: int = 204,
        response_body: Optional[Type[Any]] = None,
        model: Optional[Type[Model]] = None,
        path_parameters: Optional[Type[BaseModel]] = None,
        get_model: Optional[Callable[[HttpRequest, Optional[BaseModel]], Model]] = None,
        pre_delete: Optional[Callable[[HttpRequest, Model], None]] = None,
        post_delete: Optional[Callable[[HttpRequest, Model], None]] = None,
        decorators: Optional[
            List[Callable[[Callable[..., Any]], Callable[..., Any]]]
        ] = None,
        operation_kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            name=name,
            methods=methods or ["DELETE"],
            path=path,
            status_code=response_status,
            response_schema=response_body,
            decorators=decorators,
            operation_kwargs=operation_kwargs,
        )
        self.model = model
        self.decorators.append(self._update_handler_annotations)
        self.path_parameters = path_parameters or self.resolve_path_parameters(model)
        self.get_model = get_model or self._default_get_model
        self.pre_delete = pre_delete or (lambda request, instance: None)
        self.post_delete = post_delete or (lambda request, instance: None)

    def handler(
        self,
        request: HttpRequest,
        path_parameters: Optional[BaseModel],
    ) -> None:
        instance = self.get_model(request, path_parameters)
        self.pre_delete(request, instance)
        instance.delete()
        self.post_delete(request, instance)

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
        return cast(Type[Model], self.model).objects.get(
            **(path_parameters.model_dump() if path_parameters else {})
        )

    def as_operation(self) -> Dict[str, Any]:
        if self.api_viewset_class:
            self.model = self.model or self.api_viewset_class.model
            self.path_parameters = self.path_parameters or self.resolve_path_parameters(
                self.model
            )

        if not self.model:
            raise ValueError(
                f"Unable to determine model for view {self.name}. "
                "Please set a model either on the view or on its associated viewset."
            )

        return super().as_operation()
