from http import HTTPStatus
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Type

from django.db.models import Model
from django.http import HttpRequest
from ninja import FilterSchema, Query, Schema
from ninja.pagination import LimitOffsetPagination, PaginationBase, paginate

from ninja_crud.views.abstract_model_view import AbstractModelView
from ninja_crud.views.enums import HTTPMethod
from ninja_crud.views.helpers import utils
from ninja_crud.views.helpers.types import QuerySetGetter
from ninja_crud.views.validators.path_validator import PathValidator
from ninja_crud.views.validators.queryset_getter_validator import (
    QuerySetGetterValidator,
)

if TYPE_CHECKING:  # pragma: no cover
    from ninja_crud.viewsets import ModelViewSet


class ListModelView(AbstractModelView):
    """
    A view class that handles listing instances of a model.
    It allows customization through a queryset getter and also supports decorators.

    Example:
    ```python
    from ninja_crud import views, viewsets

    from examples.models import Department, Employee
    from examples.schemas import DepartmentOut, EmployeeOut

    class DepartmentViewSet(viewsets.ModelViewSet):
        model = Department

        # Basic usage: List all departments
        # GET /
        list_departments = views.ListModelView(response_schema=DepartmentOut)

        # Advanced usage: List employees of a specific department
        # GET /{id}/employees/
        list_employees = views.ListModelView(
            path="/{id}/employees/",
            queryset_getter=lambda id: Employee.objects.filter(department_id=id),
            response_schema=EmployeeOut,
        )
    ```

    Note:
        The attribute name (e.g., `list_departments`, `list_employees`) is flexible and customizable.
        It serves as the name of the route and the operation id in the OpenAPI schema.
    """

    def __init__(
        self,
        response_schema: Optional[Type[Schema]] = None,
        filter_schema: Optional[Type[FilterSchema]] = None,
        queryset_getter: Optional[QuerySetGetter] = None,
        pagination_class: Optional[Type[PaginationBase]] = LimitOffsetPagination,
        path: str = "/",
        decorators: Optional[List[Callable]] = None,
        router_kwargs: Optional[dict] = None,
    ) -> None:
        """
        Initializes the ListModelView.

        Args:
            response_schema (Optional[Type[Schema]], optional): The schema used to serialize the retrieved objects.
                Defaults to None. If not provided, the `default_response_schema` of the `ModelViewSet` will be used.
            filter_schema (Optional[Type[FilterSchema]], optional): The schema used to deserialize the query parameters.
                Defaults to None.
            queryset_getter (Optional[QuerySetGetter], optional): A function to customize the queryset used
                to retrieve the objects. Defaults to None.
                - If `path` has no parameters: () -> QuerySet[Model]
                - If `path` has a "{id}" parameter: (id: Any) -> QuerySet[Model]

                If not provided, the default manager of the `model` specified in the `ModelViewSet` will be used.
            pagination_class (Optional[Type[PaginationBase]], optional): The pagination class to use for the view.
                Defaults to LimitOffsetPagination.
            path (str, optional): The path to use for the view. Defaults to "/". The path may include a "{id}"
                parameter to indicate that the view is for a specific instance of the model.
            decorators (Optional[List[Callable]], optional): A list of decorators to apply to the view. Defaults to [].
            router_kwargs (Optional[dict], optional): Additional arguments to pass to the router. Defaults to {}.
                Overrides are allowed for most arguments except 'path', 'methods', and 'response'. If any of these
                arguments are provided, a warning will be logged and the override will be ignored.
        """
        super().__init__(
            method=HTTPMethod.GET,
            path=path,
            filter_schema=filter_schema,
            payload_schema=None,
            response_schema=response_schema,
            decorators=decorators,
            router_kwargs=router_kwargs,
        )

        PathValidator.validate(path=path, allow_no_parameters=True)
        QuerySetGetterValidator.validate(queryset_getter=queryset_getter, path=path)

        self.queryset_getter = queryset_getter
        self.pagination_class = pagination_class
        if self.pagination_class is not None:
            self.decorators.append(paginate(self.pagination_class))

    def build_view(self, model_class: Type[Model]) -> Callable:
        if "{id}" in self.path:
            return self._build_detail_view(model_class)
        else:
            return self._build_collection_view(model_class)

    def _build_detail_view(self, model_class: Type[Model]) -> Callable:
        filter_schema = self.filter_schema

        def detail_view(
            request: HttpRequest,
            id: utils.get_id_type(model_class),
            filters: filter_schema = Query(default=None, include_in_schema=False),
        ):
            if not model_class.objects.filter(pk=id).exists():
                raise model_class.DoesNotExist(
                    f"{model_class.__name__} with pk '{id}' does not exist."
                )

            return self.list_models(
                request=request, id=id, filters=filters, model_class=model_class
            )

        return detail_view

    def _build_collection_view(self, model_class: Type[Model]) -> Callable:
        filter_schema = self.filter_schema

        def collection_view(
            request: HttpRequest,
            filters: filter_schema = Query(default=None, include_in_schema=False),
        ):
            return self.list_models(
                request=request, id=None, filters=filters, model_class=model_class
            )

        return collection_view

    def list_models(
        self,
        request: HttpRequest,
        id: Optional[Any],
        filters: Optional[FilterSchema],
        model_class: Type[Model],
    ):
        if self.queryset_getter:
            args = [id] if "{id}" in self.path else []
            queryset = self.queryset_getter(*args)
        else:
            queryset = model_class.objects.get_queryset()

        if filters:
            queryset = filters.filter(queryset)

        return queryset

    def get_response(self) -> dict:
        """
        Provides a mapping of HTTP status codes to response schemas for the list view.

        This response schema is used in API documentation to describe the response body for this view.
        The response schema is critical and cannot be overridden using `router_kwargs`. Any overrides
        will be ignored.

        Returns:
            dict: A mapping of HTTP status codes to response schemas for the list view.
                Defaults to {200: List[self.response_schema]}. For example, for a model "Department", the response
                schema would be {200: List[DepartmentOut]}.
        """
        return {HTTPStatus.OK: List[self.response_schema]}

    def bind_to_viewset(
        self, viewset_class: Type["ModelViewSet"], model_view_name: str
    ) -> None:
        super().bind_to_viewset(viewset_class, model_view_name)
        self.bind_default_response_schema(viewset_class, model_view_name)
