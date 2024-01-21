from http import HTTPStatus
from typing import Any, Callable, Dict, List, Optional, Type

from django.db.models import QuerySet
from django.http import HttpRequest
from ninja import FilterSchema, Query, Schema
from ninja.pagination import LimitOffsetPagination, PaginationBase, paginate

from ninja_crud.views.abstract_model_view import AbstractModelView
from ninja_crud.views.enums import HTTPMethod
from ninja_crud.views.helpers import utils
from ninja_crud.views.validators.path_validator import PathValidator
from ninja_crud.views.validators.queryset_getter_validator import (
    QuerySetGetterValidator,
)


class ListModelView(AbstractModelView):
    """
    A view class that handles listing instances of a model, allowing customization
    through a queryset getter and supporting decorators.

    Args:
        path (str, optional): Path for the view. Defaults to "/". Can include a
            "{id}" parameter for a specific model instance.
        query_parameters (Optional[Type[ninja.FilterSchema]], optional): Schema for
            deserializing query parameters. Defaults to None.
        response_body (Optional[Type[List[ninja.Schema]]], optional): Schema for
            serializing the response body. Defaults to None. If not provided,
            inherits from `ModelViewSet`s `default_response_body`, wrapped in a
            List.
        queryset_getter (Optional[Callable[..., models.QuerySet]], optional):
            Customizes queryset. Defaults to None. If `path` has no parameters,
            should have the signature () -> models.QuerySet. If `path` has a "{id}"
            parameter, should have the signature (id: Any) -> models.QuerySet.
            If not provided, the default manager of the `ModelViewSet`s `model`
            will be used.
        pagination_class (Optional[Type[ninja.pagination.PaginationBase]], optional):
            Pagination class from ninja.pagination. Defaults to LimitOffsetPagination.
        decorators (Optional[List[Callable]], optional): Decorators for the view.
            Defaults to [].
        router_kwargs (Optional[Dict], optional): Additional router arguments.
            Defaults to {}. Overrides are ignored for 'path', 'methods', and
            'response'.

    Example:
    ```python
    from typing import List

    from ninja_crud import views, viewsets

    from examples.models import Department, Employee
    from examples.schemas import DepartmentOut, EmployeeOut


    class DepartmentViewSet(viewsets.ModelViewSet):
        model = Department
        default_response_body = DepartmentOut # Optional

        # Basic usage: List departments
        # Endpoint: GET /
        list_departments = views.ListModelView(response_body=List[DepartmentOut])

        # Simplified usage: Inherit default response body from ModelViewSet
        # Endpoint: GET /
        list_departments_simplified = views.ListModelView()

        # Advanced usage: List employees by department
        # Endpoint: GET /{id}/employees/
        list_department_employees = views.ListModelView(
            path="/{id}/employees/",
            queryset_getter=lambda id: Employee.objects.filter(department_id=id),
            response_body=List[EmployeeOut],
        )
    ```

    Note:
        The attribute name (e.g., `list_departments`, `list_employees`) is flexible
        and serves as the route name and operation id in the OpenAPI schema.
    """

    def __init__(
        self,
        path: str = "/",
        query_parameters: Optional[Type[FilterSchema]] = None,
        response_body: Optional[Type[List[Schema]]] = None,
        queryset_getter: Optional[Callable[..., QuerySet]] = None,
        pagination_class: Optional[Type[PaginationBase]] = LimitOffsetPagination,
        decorators: Optional[List[Callable]] = None,
        router_kwargs: Optional[Dict] = None,
    ) -> None:
        super().__init__(
            method=HTTPMethod.GET,
            path=path,
            query_parameters=query_parameters,
            request_body=None,
            response_body=response_body,
            response_status=HTTPStatus.OK,
            decorators=decorators,
            router_kwargs=router_kwargs,
        )

        PathValidator.validate(path=path, allow_no_parameters=True)
        QuerySetGetterValidator.validate(queryset_getter=queryset_getter, path=path)

        self.queryset_getter = queryset_getter
        self.pagination_class = pagination_class
        if self.pagination_class is not None:
            self.decorators.append(paginate(self.pagination_class))

    def build_view(self) -> Callable:
        if "{id}" in self.path:
            return self._build_detail_view()
        else:
            return self._build_collection_view()

    def _build_detail_view(self) -> Callable:
        model_class = self.model_viewset_class.model
        query_parameters_class = self.query_parameters

        def detail_view(
            request: HttpRequest,
            id: utils.get_id_type(model_class),
            query_parameters: query_parameters_class = Query(
                default=None, include_in_schema=False
            ),
        ):
            if not model_class.objects.filter(pk=id).exists():
                raise model_class.DoesNotExist(
                    f"{model_class.__name__} with pk '{id}' does not exist."
                )

            return self.list_models(
                request=request, id=id, query_parameters=query_parameters
            )

        return detail_view

    def _build_collection_view(self) -> Callable:
        query_parameters_class = self.query_parameters

        def collection_view(
            request: HttpRequest,
            query_parameters: query_parameters_class = Query(
                default=None, include_in_schema=False
            ),
        ):
            return self.list_models(
                request=request, id=None, query_parameters=query_parameters
            )

        return collection_view

    def list_models(
        self,
        request: HttpRequest,
        id: Optional[Any],
        query_parameters: Optional[FilterSchema],
    ):
        if self.queryset_getter:
            args = [id] if "{id}" in self.path else []
            queryset = self.queryset_getter(*args)
        else:
            queryset = self.model_viewset_class.model.objects.get_queryset()

        if query_parameters:
            queryset = query_parameters.filter(queryset)

        return queryset

    def _inherit_model_viewset_class_attributes(self) -> None:
        if self.response_body is None:
            self.response_body = List[self.model_viewset_class.default_response_body]
