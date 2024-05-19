from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Type

from django.db.models import Model, QuerySet
from django.http import HttpRequest
from ninja import FilterSchema
from ninja.pagination import LimitOffsetPagination, PaginationBase, paginate
from pydantic import BaseModel

from ninja_crud.views.api_view import APIView, ViewDecorator, ViewFunction

if TYPE_CHECKING:  # pragma: no cover
    from ninja_crud.viewsets import APIViewSet


class ListView(APIView):
    """
    Declarative class-based view for listing model instances in Django Ninja.

    This class provides a standard implementation for a list view, which retrieves
    a queryset of model instances based on path and query parameters provided in the
    URL. It is intended to be used in viewsets or as standalone views to simplify the
    creation of list endpoints.

    Args:
        method (str, optional): The HTTP method for the view. Defaults to "GET".
        path (str, optional): The URL path for the view. Defaults to "/".
        response_status (int, optional): The HTTP status code for the response.
            Defaults to 200 (OK).
        response_body (Optional[Type[Any]], optional): The response body list type.
            Defaults to None. If not provided, the default response body of the
            viewset will be used as a list type.
        view_function (Optional[ViewFunction], optional): The function that handles the
            view logic. Default implementation is `default_view_function`, which calls
            `get_queryset` to retrieve the queryset based on the request and path
            parameters, and then filters the queryset using `filter_queryset` based on
            the query parameters.
        view_function_name (Optional[str], optional): The name of the view function.
            Defaults to None, which will use the default function name. If bound to
            a viewset, the function name will be the class attribute name. Useful for
            standalone views outside viewsets.
        path_parameters (Optional[Type[BaseModel]], optional): The path parameters type.
            Defaults to None. If not provided, the default path parameters will be
            resolved based on the model, specified in the viewset or standalone view.
        query_parameters (Optional[Type[BaseModel]], optional): The query parameters
            type. Defaults to None.
        model (Optional[Type[Model]], optional): The Django model associated with the
            view. Defaults to None. Mandatory if not bound to a viewset, otherwise
            inherited from the viewset.
        decorators (Optional[List[ViewDecorator]], optional): List of decorators to
            apply to the view function. Decorators are applied in reverse order.
        operation_kwargs (Optional[Dict[str, Any]], optional): Additional keyword
            arguments for the operation.
        get_queryset (Optional[Callable], optional): A callable to retrieve the
            queryset. By default, it gets the queryset based on the model. Useful
            for customizing the queryset retrieval logic, for example, for optimizing
            queries or handling filters. Should have the signature:
            - `get_queryset(request: HttpRequest, path_parameters: Optional[BaseModel])
            -> QuerySet`.
        filter_queryset (Optional[Callable], optional): A callable to filter the
            queryset. By default, it filters the queryset based on the query parameters.
            Useful for customizing the queryset filtering logic, for example, for
            handling complex filters or permissions. Should have the signature:
            - `filter_queryset(queryset: QuerySet, query_parameters: Optional[BaseModel])
            -> QuerySet`.
        pagination_class (Optional[Type[PaginationBase]], optional): The pagination
            class to use for the view. Defaults to `LimitOffsetPagination`. If set,
            the pagination will be applied to the response. Set to `None` to disable
            pagination.

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
        model=Department,
        response_body=List[DepartmentOut],
        view_function_name="list_departments",
    ).add_view_to(api)
    ```
    """

    def __init__(
        self,
        method: str = "GET",
        path: str = "/",
        response_status: int = 200,
        response_body: Optional[Type[Any]] = None,
        view_function: Optional[ViewFunction] = None,
        view_function_name: Optional[str] = None,
        path_parameters: Optional[Type[BaseModel]] = None,
        query_parameters: Optional[Type[BaseModel]] = None,
        model: Optional[Type[Model]] = None,
        decorators: Optional[List[ViewDecorator]] = None,
        operation_kwargs: Optional[Dict[str, Any]] = None,
        get_queryset: Optional[
            Callable[[HttpRequest, Optional[BaseModel]], QuerySet[Model]]
        ] = None,
        filter_queryset: Optional[
            Callable[[QuerySet[Model], Optional[BaseModel]], QuerySet[Model]]
        ] = None,
        pagination_class: Optional[Type[PaginationBase]] = LimitOffsetPagination,
    ) -> None:
        super().__init__(
            method=method,
            path=path,
            response_status=response_status,
            response_body=response_body,
            view_function=view_function or self.default_view_function,
            view_function_name=view_function_name,
            path_parameters=path_parameters,
            query_parameters=query_parameters,
            request_body=None,
            model=model,
            decorators=decorators,
            operation_kwargs=operation_kwargs,
        )
        self.get_queryset = get_queryset or self.default_get_queryset
        self.filter_queryset = filter_queryset or self.default_filter_queryset
        self.pagination_class = pagination_class
        if self.pagination_class:
            self.decorators.append(paginate(self.pagination_class))

    def default_get_queryset(
        self, request: HttpRequest, path_parameters: Optional[BaseModel]
    ) -> QuerySet[Model]:
        """
        Default implementation of the queryset retrieval logic for the view.

        This method retrieves the queryset based on the model. By default, it gets
        all instances of the model without any filtering `Model.objects.get_queryset()`.
        It can be customized to include additional filtering using path parameters or
        for optimization purposes.
        """
        if self.model is None:
            raise ValueError("No model set for the view.")

        return self.model.objects.get_queryset()

    @staticmethod
    def default_filter_queryset(
        queryset: QuerySet[Model], query_parameters: Optional[BaseModel]
    ) -> QuerySet[Model]:
        """
        Default implementation of the filtering logic for the queryset.

        This method filters the queryset based on the query parameters. By default,
        it filters the queryset using the query parameters as keyword arguments:
        `queryset.filter(**query_parameters.dict(exclude_unset=True))` if the query
        parameters is not a `ninja.FilterSchema`. It can be customized to include
        additional filtering logic or handle complex filters.
        """
        if query_parameters is not None:
            if isinstance(query_parameters, FilterSchema):
                queryset = query_parameters.filter(queryset)
            else:
                queryset = queryset.filter(**query_parameters.dict(exclude_unset=True))
        return queryset

    def default_view_function(
        self,
        request: HttpRequest,
        path_parameters: Optional[BaseModel],
        query_parameters: Optional[BaseModel],
        request_body: Optional[BaseModel],
    ) -> QuerySet[Model]:
        """
        Default implementation of the view function for the view. It retrieves the
        queryset using `get_queryset` and then filters it using `filter_queryset`.
        """
        queryset = self.get_queryset(request, path_parameters)
        return self.filter_queryset(queryset, query_parameters)

    def set_api_viewset_class(self, api_viewset_class: Type["APIViewSet"]) -> None:
        """
        Bind the view to a viewset class.

        This method sets the model and path parameters type based on the viewset class,
        and assigns the response body from the viewset class's `default_response_body`
        as a list type if the response body is not already set.

        Note:
            This method is called internally and automatically by the viewset when
            defining views as class attributes. It should not be called manually.
        """
        super().set_api_viewset_class(api_viewset_class)

        if self.response_body is None:
            self.response_body = List[api_viewset_class.default_response_body]  # type: ignore[name-defined]
