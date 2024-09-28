from types import FunctionType
from typing import Any, Callable, Dict, List, Optional, Type, cast

from django.db.models import Model, QuerySet
from django.http import HttpRequest
from ninja import FilterSchema
from ninja.pagination import LimitOffsetPagination, PaginationBase, paginate
from ninja.params.functions import Path, Query
from pydantic import BaseModel
from typing_extensions import Annotated

from ninja_crud.views.api_view import APIView


class ListView(APIView):
    """
    Declarative class-based view for listing model instances in Django Ninja.

    This class provides a standard implementation for a list view, which retrieves
    a queryset of model instances based on path and query parameters provided in the
    URL. It is intended to be used in viewsets or as standalone views to simplify the
    creation of list endpoints.

    Args:
        name (str | None, optional): View function name. Defaults to `None`. If None,
            uses class attribute name in viewsets or "handler" for standalone views.
        methods (List[str], optional): HTTP methods. Defaults to `["GET"]`.
        path (str, optional): URL path. Defaults to `"/"`.
        response_status (int, optional): HTTP response status code. Defaults to `200`.
        response_body (Type | None, optional): Response body type. Defaults to `None`.
            If None, uses the default response body of the viewset as a list type.
        path_parameters (Type[BaseModel] | None, optional): Path parameters type.
            Defaults to `None`. If not provided, resolved from the path and model.
        query_parameters (Type[BaseModel] | None, optional): Query parameters type.
            Defaults to `None`.
        model (Type[django.db.models.Model] | None, optional): Associated Django model.
            Inherits from viewset if not provided. Defaults to `None`.
        get_queryset (Callable | None, optional): Callable to retrieve the queryset.
            Default uses `self.model.objects.get_queryset()`. Useful for selecting
            related models or optimizing queries. Should have the signature:
            - `(request: HttpRequest, path_parameters: Optional[BaseModel]) -> QuerySet`
        filter_queryset (Callable | None, optional): Callable to filter the queryset.
            Default uses `query_parameters.filter(queryset)` if `query_parameters` is a
            `ninja.FilterSchema`, otherwise filters the queryset based on the query
            parameters as keyword arguments:
            `queryset.filter(**query_parameters.model_dump(exclude_unset=True))`.
            Should have the signature:
            - `(queryset: QuerySet, query_parameters: Optional[BaseModel]) -> QuerySet`
        pagination_class (Type[PaginationBase] | None, optional): Pagination class.
            Defaults to `LimitOffsetPagination`. If None, no pagination is applied.
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

        list_departments = views.ListView()

    # Usage as a standalone view:
    views.ListView(
        name="list_departments",
        model=Department,
        response_body=List[DepartmentOut],
    ).add_view_to(api)
    ```
    """

    def __init__(
        self,
        name: Optional[str] = None,
        methods: Optional[List[str]] = None,
        path: str = "/",
        response_status: int = 200,
        response_body: Optional[Type[Any]] = None,
        model: Optional[Type[Model]] = None,
        path_parameters: Optional[Type[BaseModel]] = None,
        query_parameters: Optional[Type[BaseModel]] = None,
        get_queryset: Optional[
            Callable[[HttpRequest, Optional[BaseModel]], QuerySet[Model]]
        ] = None,
        filter_queryset: Optional[
            Callable[[QuerySet[Model], Optional[BaseModel]], QuerySet[Model]]
        ] = None,
        pagination_class: Optional[Type[PaginationBase]] = LimitOffsetPagination,
        decorators: Optional[
            List[Callable[[Callable[..., Any]], Callable[..., Any]]]
        ] = None,
        operation_kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            name=name,
            methods=methods or ["GET"],
            path=path,
            response_status=response_status,
            response_body=response_body,
            model=model,
            decorators=decorators,
            operation_kwargs=operation_kwargs,
        )
        self.decorators.append(self._update_handler_annotations)
        self.path_parameters = path_parameters or self.resolve_path_parameters()
        self.query_parameters = query_parameters
        self.get_queryset = get_queryset or self._default_get_queryset
        self.filter_queryset = filter_queryset or self._default_filter_queryset
        self.pagination_class = pagination_class
        if self.pagination_class:
            self.decorators.append(paginate(self.pagination_class))

    def handler(
        self,
        request: HttpRequest,
        path_parameters: Optional[BaseModel],
        query_parameters: Optional[BaseModel],
    ) -> QuerySet[Model]:
        queryset = self.get_queryset(request, path_parameters)
        return self.filter_queryset(queryset, query_parameters)

    def _update_handler_annotations(
        self, handler: Callable[..., Any]
    ) -> Callable[..., Any]:
        annotations = cast(FunctionType, handler).__annotations__
        annotations["path_parameters"] = Annotated[
            self.path_parameters, Path(default=None, include_in_schema=False)
        ]
        annotations["query_parameters"] = Annotated[
            self.query_parameters, Query(default=None, include_in_schema=False)
        ]
        return handler

    def _default_get_queryset(
        self, request: HttpRequest, path_parameters: Optional[BaseModel]
    ) -> QuerySet[Model]:
        return cast(Type[Model], self.model).objects.get_queryset()

    def _default_filter_queryset(
        self, queryset: QuerySet[Model], query_parameters: Optional[BaseModel]
    ) -> QuerySet[Model]:
        if query_parameters is not None:
            if isinstance(query_parameters, FilterSchema):
                queryset = query_parameters.filter(queryset)
            else:
                queryset = queryset.filter(
                    **query_parameters.model_dump(exclude_unset=True)
                )
        return queryset

    def as_operation(self) -> Dict[str, Any]:
        if self.api_viewset_class:
            self.model = self.model or self.api_viewset_class.model
            self.path_parameters = (
                self.path_parameters or self.resolve_path_parameters()
            )
            self.response_body = (
                self.response_body or List[self.api_viewset_class.default_response_body]  # type: ignore[name-defined]
            )

        if not self.model:
            raise ValueError(
                f"Unable to determine model for view {self.name}. "
                "Please set a model either on the view or on its associated viewset."
            )

        return super().as_operation()
