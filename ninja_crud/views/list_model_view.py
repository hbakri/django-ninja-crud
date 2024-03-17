import http
from typing import Callable, Dict, List, Optional, Type

from django.db.models import QuerySet
from django.http import HttpRequest
from ninja import FilterSchema, Schema
from ninja.pagination import LimitOffsetPagination, PaginationBase, paginate

from ninja_crud.views.abstract_model_view import AbstractModelView
from ninja_crud.views.enums import HTTPMethod


class ListModelView(AbstractModelView):
    """
    A view class that handles listing model instances.

    Designed to be used as an attribute of a
    [`ninja_crud.viewsets.ModelViewSet`](https://django-ninja-crud.readme.io/reference/model-viewset),
    this class should not be used directly as a standalone view. It is crafted for
    flexibility and allows extensive customization through overrideable methods for
    actions including but not limited to permission checks, advanced queryset retrieval
    and filtering. Subclassing is recommended to encapsulate repetitive customizations.

    Args:
        path (str, optional): View path. Defaults to `"/"`.
        path_parameters (Optional[Type[ninja.Schema]], optional): Schema for
            deserializing path parameters. By default, it is automatically inferred from
            the path and the fields of the ModelViewSet's associated model. Defaults to
            `None`.
        query_parameters (Optional[Type[ninja.Schema]], optional): Schema for
            deserializing query parameters. Defaults to `None`. For advanced query
            filtering, it supports the use of
            [FilterSchema](https://django-ninja.dev/guides/input/filtering/).
        response_body (Optional[Type[ninja.Schema]], optional): Schema for serializing
            the response body. By default, it inherits the ModelViewSet's default
            response body. Defaults to `None`.
        decorators (Optional[List[Callable]], optional): Decorators for the view.
            Defaults to `[]`.
        router_kwargs (Optional[Dict], optional): Additional router arguments, with
            overrides for 'path', 'methods', and 'response' being ignored. Defaults
            to `{}`.
        get_queryset (Optional[Callable], optional): Function to retrieve the queryset
            based on the request and path parameters. This method can be overridden with
            custom logic to retrieve the queryset, allowing for advanced retrieval
            logic, such as adding annotations, filtering based on request specifics, or
            implementing permissions checks, to suit specific requirements and
            potentially improve efficiency and security. By default, it retrieves the
            queryset using the ModelViewSet's model and the path parameters.
            Should have the signature:
            - `(request: HttpRequest, path_parameters: Optional[Schema]) -> QuerySet`.
        filter_queryset (Optional[Callable], optional): Function to filter the queryset
            based on the retrieved queryset and query parameters. This method can be
            overridden with custom logic to filter the queryset if the default behavior
            is insufficient. By default, if the query parameters schema is a
            `FilterSchema`, it filters the queryset using the schema's `filter()`
            method; otherwise, it filters the queryset using the query parameters as
            keyword arguments. Should have the signature:
            - `(queryset: QuerySet, query_parameters: Optional[Schema]) -> QuerySet`.
        list_models (Optional[Callable], optional): Function to list the model instances
            based on the request, path parameters, and query parameters. This method can
            be overridden with custom logic, allowing for advanced listing logic, such
            as implementing additional checks, or permissions checks, to suit specific
            requirements. By default, it calls `get_queryset` and `filter_queryset`.
            When overriding this method, note that the get_queryset and filter_queryset
            methods are not called anymore. Should have the signature:
            - `(request: HttpRequest, path_parameters: Optional[Schema],
                query_parameters: Optional[Schema]) -> QuerySet`.
        pagination_class (Optional[Type[ninja.pagination.PaginationBase]], optional):
            Pagination class. Defaults to [`ninja.pagination.LimitOffsetPagination`](
            https://django-ninja.dev/guides/response/pagination/).

    Raises:
        ninja.errors.ValidationError: For request components validation issues.

    Since this view does not automatically handle exceptions, implementation requires
    appropriate [exception handlers](https://django-ninja.dev/guides/errors/) for
    comprehensive error management according to your application's conventions.
    Refer to the [setup guide](https://django-ninja-crud.readme.io/docs/03-setup).

    Example:
    ```python
    class DepartmentViewSet(viewsets.ModelViewSet):
        model = Department

        # Basic usage with implicit default settings
        list_departments = views.ListModelView(
            response_body=List[DepartmentOut]
        )

        # Basic usage with explicit default settings
        list_departments = views.ListModelView(
            path="/",
            response_body=List[DepartmentOut],
            get_queryset=lambda request, path_parameters: Department.objects.all(),
            pagination_class=ninja.pagination.LimitOffsetPagination,
        )

        # Usage with default response body schema set in the ModelViewSet
        default_response_body = DepartmentOut
        list_departments = views.ListModelView()

        # Custom query parameters schema for advanced filtering
        list_departments = views.ListModelView(
            query_parameters=DepartmentFilterSchema,
            response_body=List[DepartmentOut],
        )

        # Custom queryset retrieval for annotated fields or any advanced logic
        list_departments = views.ListModelView(
            response_body=List[DepartmentOut],
            get_queryset=lambda request, path_parameters: Department.objects.annotate(
                count_employees=Count("employees")
            ),
        )

        # Custom pagination class
        list_departments = views.ListModelView(
            response_body=List[DepartmentOut],
            pagination_class=ninja.pagination.PageNumberPagination,
        )

        # Authentication at the view level
        list_departments = views.ListModelView(
            response_body=List[DepartmentOut],
            router_kwargs={"auth": ninja.security.django_auth},
        )

        # Advanced usage with external service
        list_departments = views.ListModelView(
            response_body=List[DepartmentOut],
            list_models=lambda request, path_parameters, query_parameters: external_service.list_departments(
                ...
            ),
        )
    ```

    Note:
        The name of the class attribute (e.g., `list_departments`) determines the
        route's name and operation ID in the OpenAPI schema. Can be any valid Python
        attribute name, but it is recommended to use a name that reflects the action
        being performed.
    """

    def __init__(
        self,
        path: str = "/",
        path_parameters: Optional[Type[Schema]] = None,
        query_parameters: Optional[Type[Schema]] = None,
        response_body: Optional[Type[List[Schema]]] = None,
        decorators: Optional[List[Callable]] = None,
        router_kwargs: Optional[Dict] = None,
        get_queryset: Optional[
            Callable[[HttpRequest, Optional[Schema]], QuerySet]
        ] = None,
        filter_queryset: Optional[
            Callable[[QuerySet, Optional[Schema]], QuerySet]
        ] = None,
        list_models: Optional[
            Callable[[HttpRequest, Optional[Schema], Optional[Schema]], QuerySet]
        ] = None,
        pagination_class: Optional[Type[PaginationBase]] = LimitOffsetPagination,
    ) -> None:
        super().__init__(
            method=HTTPMethod.GET,
            path=path,
            path_parameters=path_parameters,
            query_parameters=query_parameters,
            request_body=None,
            response_body=response_body,
            response_status=http.HTTPStatus.OK,
            decorators=decorators,
            router_kwargs=router_kwargs,
        )
        self.get_queryset = get_queryset or self._default_get_queryset
        self.filter_queryset = filter_queryset or self._default_filter_queryset
        self.list_models = list_models or self._default_list_models
        self.pagination_class = pagination_class
        if self.pagination_class:
            self.decorators.append(paginate(self.pagination_class))

    def _default_get_queryset(
        self, request: HttpRequest, path_parameters: Optional[Schema]
    ) -> QuerySet:
        return self.model_viewset_class.model.objects.get_queryset()

    @staticmethod
    def _default_filter_queryset(
        queryset: QuerySet,
        query_parameters: Optional[Schema],
    ) -> QuerySet:
        if query_parameters:
            if isinstance(query_parameters, FilterSchema):
                queryset = query_parameters.filter(queryset)
            else:
                queryset = queryset.filter(**query_parameters.dict(exclude_unset=True))
        return queryset

    def _default_list_models(
        self,
        request: HttpRequest,
        path_parameters: Optional[Schema],
        query_parameters: Optional[Schema],
    ) -> QuerySet:
        queryset = self.get_queryset(request, path_parameters)
        return self.filter_queryset(queryset, query_parameters)

    def handle_request(
        self,
        request: HttpRequest,
        path_parameters: Optional[Schema],
        query_parameters: Optional[Schema],
        request_body: Optional[Schema],
    ) -> QuerySet:
        return self.list_models(request, path_parameters, query_parameters)

    def _inherit_model_viewset_class_attributes(self) -> None:
        if self.response_body is None:
            default_response_body = self.model_viewset_class.default_response_body
            self.response_body = List[default_response_body]  # type: ignore
