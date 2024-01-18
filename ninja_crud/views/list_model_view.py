from http import HTTPStatus
from typing import Any, Callable, Dict, List, Optional, Type, get_args, get_origin

import ninja
from django.db.models import Model
from django.http import HttpRequest
from ninja.pagination import LimitOffsetPagination, PaginationBase, paginate

from ninja_crud.views.abstract_model_view import AbstractModelView
from ninja_crud.views.enums import HTTPMethod
from ninja_crud.views.helpers import utils
from ninja_crud.views.helpers.types import QuerySetGetter
from ninja_crud.views.validators.path_validator import PathValidator
from ninja_crud.views.validators.queryset_getter_validator import (
    QuerySetGetterValidator,
)


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
        path: str = "/",
        query_parameters: Optional[Type[ninja.FilterSchema]] = None,
        response_body: Optional[Type[List[ninja.Schema]]] = None,
        queryset_getter: Optional[QuerySetGetter] = None,
        pagination_class: Optional[Type[PaginationBase]] = LimitOffsetPagination,
        decorators: Optional[List[Callable]] = None,
        router_kwargs: Optional[Dict] = None,
    ) -> None:
        """
        Initializes the ListModelView.

        Args:
            path (str, optional): The path to use for the view. Defaults to "/". The
                path may include a "{id}" parameter to indicate that the view is for
                a specific instance of the model.
            query_parameters (Optional[Type[ninja.FilterSchema]], optional): The
                schema used to deserialize the query parameters. Defaults to None.
            response_body (Optional[Type[List[ninja.Schema]]], optional): The schema
                used to serialize the response body. Defaults to None. If not provided,
                the `default_response_body` of the `ModelViewSet` will be used.
            queryset_getter (Optional[QuerySetGetter], optional): A function to customize the queryset used
                to retrieve the objects. Defaults to None.
                - If `path` has no parameters: () -> QuerySet[Model]
                - If `path` has a "{id}" parameter: (id: Any) -> QuerySet[Model]

                If not provided, the default manager of the `model` specified in the `ModelViewSet` will be used.
            pagination_class (Optional[Type[PaginationBase]], optional): The
                pagination class to use for the view. Defaults to LimitOffsetPagination.
            decorators (Optional[List[Callable]], optional): A list of decorators
                to apply to the view. Defaults to [].
            router_kwargs (Optional[Dict], optional): Additional arguments to pass
                to the router. Defaults to {}. Overrides are allowed for most
                arguments except 'path', 'methods', and 'response'. If any of these
                arguments are provided, a warning will be logged and the override
                will be ignored.
        """
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
        # TODO: type-check query_parameters as a subclass of ninja.FilterSchema
        # TODO: type-check pagination_class as a subclass of ninja.PaginationBase

        PathValidator.validate(path=path, allow_no_parameters=True)
        QuerySetGetterValidator.validate(queryset_getter=queryset_getter, path=path)

        self.queryset_getter = queryset_getter
        self.pagination_class = pagination_class
        if self.pagination_class is not None:
            self.decorators.append(paginate(self.pagination_class))

    @staticmethod
    def _validate_response_body(
        response_body: Optional[Type[List[ninja.Schema]]],
    ) -> None:
        if response_body is not None:
            is_valid_list_of_schema = (
                get_origin(response_body) is list
                and len(get_args(response_body)) == 1
                and issubclass(get_args(response_body)[0], ninja.Schema)
            )
            if not is_valid_list_of_schema:
                raise TypeError(
                    f"Expected 'response_body' to be a list of a single subclass of "
                    f"ninja.Schema, but found type {type(response_body)}."
                )

    def build_view(self) -> Callable:
        model_class = self.model_viewset_class.model
        if "{id}" in self.path:
            return self._build_detail_view(model_class)
        else:
            return self._build_collection_view(model_class)

    def _build_detail_view(self, model_class: Type[Model]) -> Callable:
        query_parameters = self.query_parameters

        def detail_view(
            request: HttpRequest,
            id: utils.get_id_type(model_class),
            filters: query_parameters = ninja.Query(
                default=None, include_in_schema=False
            ),
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
        query_parameters = self.query_parameters

        def collection_view(
            request: HttpRequest,
            filters: query_parameters = ninja.Query(
                default=None, include_in_schema=False
            ),
        ):
            return self.list_models(
                request=request, id=None, filters=filters, model_class=model_class
            )

        return collection_view

    def list_models(
        self,
        request: HttpRequest,
        id: Optional[Any],
        filters: Optional[ninja.FilterSchema],
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

    def _inherit_model_viewset_class_attributes(self) -> None:
        if self.response_body is None:
            self.response_body = List[self.model_viewset_class.default_response_body]
