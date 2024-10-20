from types import FunctionType
from typing import Annotated, Any, Callable, Optional, Union, cast

from django.db.models import Model, QuerySet
from django.http import HttpRequest
from ninja import FilterSchema
from ninja.pagination import LimitOffsetPagination, PaginationBase, paginate
from ninja.params.functions import Path, Query
from pydantic import BaseModel

from ninja_crud.views.api_view import APIView
from ninja_crud.views.types import Decorator, QuerySetFilter, QuerySetGetter


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
        methods (list[str] | set[str], optional): HTTP methods. Defaults to `["GET"]`.
        path (str, optional): URL path. Defaults to `"/"`.
        response_status (int, optional): HTTP response status code. Defaults to `200`.
        response_body (Any, optional): Response body type. Defaults to `None`.
            If None, uses the default response body of the viewset as a list type.
        model (type[django.db.models.Model], optional): Associated Django model.
            Inherits from viewset if not provided. Defaults to `None`.
        path_parameters (type[BaseModel], optional): Path parameters type.
            Defaults to `None`. If not provided, resolved from the path and model.
        query_parameters (type[BaseModel], optional): Query parameters type.
            Defaults to `None`.
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
            - `(queryset: QuerySet, query_parameters: BaseModel | None) -> QuerySet`
        pagination_class (type[PaginationBase], optional): Pagination class.
            Defaults to `LimitOffsetPagination`. If None, pagination is disabled.
        decorators (list[Callable], optional): View function decorators
            (applied in reverse order). Defaults to `None`.
        operation_kwargs (dict[str, Any], optional): Additional operation
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
        list_departments = views.ListView()

        # Usage with explicit response body:
        list_departments = views.ListView(response_body=list[DepartmentOut])

    # Usage as a standalone view:
    views.ListView(
        name="list_departments",
        model=Department,
        response_body=list[DepartmentOut],
    ).add_view_to(api)
    ```
    """

    def __init__(
        self,
        name: Optional[str] = None,
        methods: Union[list[str], set[str], None] = None,
        path: str = "/",
        response_status: int = 200,
        response_body: Any = None,
        model: Optional[type[Model]] = None,
        path_parameters: Optional[type[BaseModel]] = None,
        query_parameters: Optional[type[BaseModel]] = None,
        get_queryset: Optional[QuerySetGetter] = None,
        filter_queryset: Optional[QuerySetFilter] = None,
        pagination_class: Optional[type[PaginationBase]] = LimitOffsetPagination,
        decorators: Optional[list[Decorator]] = None,
        operation_kwargs: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            name=name,
            methods=methods or ["GET"],
            path=path,
            status_code=response_status,
            response_schema=response_body,
            decorators=decorators,
            operation_kwargs=operation_kwargs,
        )
        self.model = model
        self.decorators.append(self._update_handler_annotations)
        self.path_parameters = path_parameters
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
        return cast(type[Model], self.model).objects.get_queryset()

    def _default_filter_queryset(
        self, queryset: QuerySet[Model], query_parameters: Optional[BaseModel]
    ) -> QuerySet[Model]:
        if isinstance(query_parameters, FilterSchema):
            queryset = query_parameters.filter(queryset)
        elif isinstance(query_parameters, BaseModel):
            queryset = queryset.filter(
                **query_parameters.model_dump(exclude_unset=True)
            )
        return queryset

    def as_operation(self) -> dict[str, Any]:
        if self.api_viewset_class:
            self.model = self.model or self.api_viewset_class.model
            self.response_schema = (
                self.response_schema
                or list[self.api_viewset_class.default_response_body]  # type: ignore[name-defined]
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
