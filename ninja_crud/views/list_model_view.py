from http import HTTPStatus
from typing import Any, Callable, Dict, List, Optional, Type, Union

from django.db.models import QuerySet
from django.http import HttpRequest
from ninja import FilterSchema, Schema
from ninja.pagination import LimitOffsetPagination, PaginationBase, paginate

from ninja_crud.views.abstract_model_view import AbstractModelView
from ninja_crud.views.enums import HTTPMethod
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
            inherits from `ModelViewSet`s `default_response_body`, wrapped in a List.
        queryset_getter (Union[Callable[[], models.QuerySet],
            Callable[[Any], models.QuerySet], None], optional): Customizes queryset.
            Defaults to None. If `path` has no parameters, should have the signature
            () -> QuerySet. If `path` has a "{id}" parameter, (id: Any) -> QuerySet.
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
        list_departments = views.ListModelView()

        # Advanced usage: List employees by department
        # Endpoint: GET /{id}/employees/
        list_employees = views.ListModelView(
            path="/{id}/employees/",
            response_body=List[EmployeeOut],
            queryset_getter=lambda id: Employee.objects.filter(department_id=id),
        )
    ```

    Note:
        The attribute name (e.g., `list_departments`) is flexible and customizable.
        It serves as the name of the route and the operation id in the OpenAPI schema.
    """

    def __init__(
        self,
        path: str = "/",
        query_parameters: Optional[Type[Schema]] = None,
        response_body: Optional[Type[List[Schema]]] = None,
        queryset_getter: Union[
            Callable[[], QuerySet], Callable[[Any], QuerySet], None
        ] = None,
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
        if self.pagination_class:
            self.decorators.append(paginate(self.pagination_class))

    def handle_request(
        self,
        request: HttpRequest,
        path_parameters: Optional[Schema],
        query_parameters: Optional[Schema],
        request_body: Optional[Schema],
    ) -> QuerySet:
        if path_parameters:
            self.model_viewset_class.model.objects.get(**path_parameters.dict())

        if self.queryset_getter:
            queryset_getter_kwargs = path_parameters.dict() if path_parameters else {}
            queryset = self.queryset_getter(**queryset_getter_kwargs)
        else:
            queryset = self.model_viewset_class.model.objects.get_queryset()

        if query_parameters:
            if isinstance(query_parameters, FilterSchema):
                queryset = query_parameters.filter(queryset)
            else:
                queryset = queryset.filter(**query_parameters.dict(exclude_unset=True))

        return queryset

    def _inherit_model_viewset_class_attributes(self) -> None:
        if self.response_body is None:
            self.response_body = List[self.model_viewset_class.default_response_body]
