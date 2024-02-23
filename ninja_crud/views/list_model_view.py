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

    Args:
        path (str, optional): View path. Defaults to "/{id}".
        path_parameters (Optional[Type[ninja.Schema]], optional): Schema for
            deserializing path parameters. Automatically inferred from the path
            and the fields of the `ModelViewSet`'s associated model if not provided.
            Defaults to None.
        query_parameters (Optional[Type[ninja.Schema]], optional): Schema for
            deserializing query parameters. Defaults to None.
        response_body (Optional[Type[List[ninja.Schema]]], optional): Schema for
            serializing the response body. Inherits `ModelViewSet`'s default if
            unspecified. Defaults to None.
        get_queryset (Optional[Callable[[Optional[ninja.Schema]],
            django.db.models.QuerySet]], optional):
            Function to retrieve the queryset. Defaults to `default_get_queryset`.
            Should have the signature (path_parameters: Optional[Schema]) -> QuerySet.
        pagination_class (Optional[Type[ninja.pagination.PaginationBase]], optional):
            Pagination class. Defaults to `ninja.pagination.LimitOffsetPagination`.
        decorators (Optional[List[Callable]], optional): Decorators for the view.
            Defaults to [].
        router_kwargs (Optional[Dict], optional): Additional router arguments, with
            overrides for 'path', 'methods', and 'response' being ignored. Defaults
            to {}.

    Raises:
        ninja.errors.ValidationError: For request components validation issues.

    Important:
        This view does not automatically handle exceptions. It's recommended to
        implement appropriate
        [Exception Handlers](https://django-ninja.dev/guides/errors/) in your project to
        manage such cases effectively, according to your application's needs and
        conventions. See the [Setup](https://django-ninja-crud.readme.io/docs/03-setup)
        guide for more information.

    Example Usage:
    ```python
    # Basic usage using response schema
    list_departments = views.ListModelView(
        response_body=List[DepartmentResponseBody],
    )

    # Advanced usage with custom get_queryset logic
    list_departments = views.ListModelView(
        response_body=List[DepartmentResponseBody],
        get_queryset=lambda path_parameters: Department.objects.all(),
    )
    ```

    Note:
        The attribute name (e.g., `list_departments`) determines the route's name
        and operation ID in the OpenAPI schema, allowing easy API documentation.
    """

    def __init__(
        self,
        path: str = "/",
        path_parameters: Optional[Type[Schema]] = None,
        query_parameters: Optional[Type[Schema]] = None,
        response_body: Optional[Type[List[Schema]]] = None,
        get_queryset: Optional[Callable[[Optional[Schema]], QuerySet]] = None,
        pagination_class: Optional[Type[PaginationBase]] = LimitOffsetPagination,
        decorators: Optional[List[Callable]] = None,
        router_kwargs: Optional[Dict] = None,
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
        self.get_queryset = get_queryset or self.default_get_queryset
        self.pagination_class = pagination_class
        if self.pagination_class:
            self.decorators.append(paginate(self.pagination_class))

    def default_get_queryset(
        self,
        path_parameters: Optional[Schema],
    ) -> QuerySet:
        """
        Default function to retrieve the queryset.

        This method can be overridden with custom logic to retrieve the queryset,
        allowing for advanced retrieval logic, such as adding annotations, filtering
        based on request specifics, or implementing permissions checks, to suit specific
        requirements and potentially improve efficiency and security.

        Args:
            path_parameters (Optional[ninja.Schema]): Deserialized path parameters.

        Returns:
            django.db.models.QuerySet: The queryset to be retrieved.
        """
        return self.model_viewset_class.model.objects.get_queryset()

    @staticmethod
    def filter_queryset(
        queryset: QuerySet,
        query_parameters: Optional[Schema],
    ) -> QuerySet:
        if query_parameters:
            if isinstance(query_parameters, FilterSchema):
                queryset = query_parameters.filter(queryset)
            else:
                queryset = queryset.filter(**query_parameters.dict(exclude_unset=True))
        return queryset

    def handle_request(
        self,
        request: HttpRequest,
        path_parameters: Optional[Schema],
        query_parameters: Optional[Schema],
        request_body: Optional[Schema],
    ) -> QuerySet:
        if path_parameters:
            self.model_viewset_class.model.objects.get(**path_parameters.dict())

        queryset = self.get_queryset(path_parameters)
        return self.filter_queryset(queryset, query_parameters)

    def _inherit_model_viewset_class_attributes(self) -> None:
        if self.response_body is None:
            default_response_body = self.model_viewset_class.default_response_body
            self.response_body = List[default_response_body]  # type: ignore
