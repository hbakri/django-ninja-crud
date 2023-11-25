from http import HTTPStatus
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Type, Union

from django.db.models import Model
from django.http import HttpRequest
from ninja import FilterSchema, Query, Router, Schema
from ninja.pagination import LimitOffsetPagination, PaginationBase, paginate

from ninja_crud.views.abstract_model_view import AbstractModelView
from ninja_crud.views.enums import HTTPMethod
from ninja_crud.views.helpers import utils
from ninja_crud.views.helpers.types import (
    CollectionQuerySetGetter,
    DetailQuerySetGetter,
)
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
        # GET /departments/
        list_departments_view = views.ListModelView(output_schema=DepartmentOut)

        # Advanced usage: List employees of a specific department
        # GET /departments/{id}/employees/
        list_employees_view = views.ListModelView(
            detail=True,
            queryset_getter=lambda id: Employee.objects.filter(department_id=id),
            output_schema=EmployeeOut,
        )
    ```
    """

    def __init__(
        self,
        output_schema: Optional[Type[Schema]] = None,
        filter_schema: Optional[Type[FilterSchema]] = None,
        detail: bool = False,
        queryset_getter: Union[
            DetailQuerySetGetter, CollectionQuerySetGetter, None
        ] = None,
        pagination_class: Optional[Type[PaginationBase]] = LimitOffsetPagination,
        path: Optional[str] = None,
        decorators: Optional[List[Callable]] = None,
        router_kwargs: Optional[dict] = None,
    ) -> None:
        """
        Initializes the ListModelView.

        Args:
            output_schema (Optional[Type[Schema]], optional): The schema used to serialize the retrieved objects.
                Defaults to None. If not provided, the `default_output_schema` of the `ModelViewSet` will be used.
            filter_schema (Optional[Type[FilterSchema]], optional): The schema used to validate the filters.
            detail (bool, optional): Whether the view is a detail or collection view. Defaults to False.

                If set to True, `queryset_getter` must be provided.
            queryset_getter (Union[DetailQuerySetGetter, CollectionQuerySetGetter, None], optional): A
                function to customize the queryset used for retrieving the objects. Defaults to None.
                The function should have one of the following signatures:
                - For `detail=False`: () -> QuerySet[Model]
                - For `detail=True`: (id: Any) -> QuerySet[Model]

                If not provided, the default manager of the `model` specified in the `ModelViewSet` will be used.
            pagination_class (Optional[Type[PaginationBase]], optional): The pagination class to use for the view.
                Defaults to LimitOffsetPagination.
            path (Optional[str], optional): The path to use for the view. Defaults to:
                - For `detail=False`: "/"
                - For `detail=True`: "/{id}/{related_model_name_plural_to_snake_case}/"

                Where `related_model_name_plural_to_snake_case` refers to the plural form of the related model's name,
                converted to snake_case. For example, for a related model "ItemDetail", the path might look like
                "/{id}/item_details/".
            decorators (Optional[List[Callable]], optional): A list of decorators to apply to the view. Defaults to [].
            router_kwargs (Optional[dict], optional): Additional arguments to pass to the router. Defaults to {}.
                Overrides are allowed for most arguments except 'path', 'methods', and 'response'. If any of these
                arguments are provided, a warning will be logged and the override will be ignored.
        """
        if detail and queryset_getter is None:
            raise ValueError(
                "Expected 'queryset_getter' when 'detail=True', but found None."
            )
        QuerySetGetterValidator.validate(queryset_getter, detail)
        queryset_getter_model_class: Optional[Type[Model]] = (
            queryset_getter(None).model if detail else None
        )

        if path is None:
            path = self._get_default_path(
                detail=detail, model_class=queryset_getter_model_class
            )
        self.pagination_class = pagination_class
        if pagination_class is not None:
            decorators = decorators or []
            decorators.append(paginate(pagination_class))
        super().__init__(
            method=HTTPMethod.GET,
            path=path,
            detail=detail,
            decorators=decorators,
            router_kwargs=router_kwargs,
        )

        self.output_schema = output_schema
        self.filter_schema = filter_schema
        self.queryset_getter = queryset_getter
        self._related_model_class = queryset_getter_model_class

    def register_route(self, router: Router, model_class: Type[Model]) -> None:
        if self.detail:
            self._register_detail_route(router, model_class)
        else:
            self._register_collection_route(router, model_class)

    def _register_detail_route(self, router: Router, model_class: Type[Model]) -> None:
        filter_schema = self.filter_schema

        @self.configure_route(router=router, model_class=model_class)
        def list_models(
            request: HttpRequest,
            id: utils.get_id_type(model_class),
            filters: filter_schema = Query(default=FilterSchema()),
        ):
            if not model_class.objects.filter(pk=id).exists():
                raise model_class.DoesNotExist(
                    f"{model_class.__name__} with pk '{id}' does not exist."
                )

            return self.list_models(
                request=request, id=id, filters=filters, model_class=model_class
            )

    def _register_collection_route(
        self, router: Router, model_class: Type[Model]
    ) -> None:
        filter_schema = self.filter_schema

        @self.configure_route(router=router, model_class=model_class)
        def list_models(
            request: HttpRequest, filters: filter_schema = Query(default=FilterSchema())
        ):
            return self.list_models(
                request=request, id=None, filters=filters, model_class=model_class
            )

    def list_models(
        self,
        request: HttpRequest,
        id: Optional[Any],
        filters: FilterSchema,
        model_class: Type[Model],
    ):
        if self.queryset_getter:
            args = [id] if self.detail else []
            queryset = self.queryset_getter(*args)
        else:
            queryset = model_class.objects.get_queryset()

        order_by_filters = filters.dict().pop("order_by", None)
        if order_by_filters is not None:
            queryset = queryset.order_by(*order_by_filters)

        return filters.filter(queryset)

    @staticmethod
    def _get_default_path(detail: bool, model_class: Type[Model]) -> str:
        if detail:
            related_model_name = utils.to_snake_case(model_class.__name__)
            return f"/{{id}}/{related_model_name}s/"
        else:
            return "/"

    def get_response(self) -> dict:
        """
        Provides a mapping of HTTP status codes to response schemas for the list view.

        This response schema is used in API documentation to describe the response body for this view.
        The response schema is critical and cannot be overridden using `router_kwargs`. Any overrides
        will be ignored.

        Returns:
            dict: A mapping of HTTP status codes to response schemas for the list view.
                Defaults to {200: List[self.output_schema]}. For example, for a model "Department", the response
                schema would be {200: List[DepartmentOut]}.
        """
        return {HTTPStatus.OK: List[self.output_schema]}

    def get_operation_id(self, model_class: Type[Model]) -> str:
        """
        Provides an operation ID for the list view.

        This operation ID is used in API documentation to uniquely identify this view.
        It can be overriden using the `router_kwargs`.

        Args:
            model_class (Type[Model]): The Django model class associated with this view.

        Returns:
            str: The operation ID for the list view. Defaults to:
                - For `detail=False`: "list_{model_name_to_snake_case}s". For example, for a model "Department",
                    the operation ID would be "list_departments".
                - For `detail=True`: "list_{model_name_to_snake_case}_{related_model_name_to_snake_case}s". For
                    example, for a model "Department" with a related model "Item", the operation ID would be
                    "list_department_items".
        """
        model_name = utils.to_snake_case(model_class.__name__)
        if self.detail:
            related_model_name = utils.to_snake_case(self._related_model_class.__name__)
            return f"list_{model_name}_{related_model_name}s"
        else:
            return f"list_{model_name}s"

    def get_summary(self, model_class: Type[Model]) -> str:
        """
        Provides a summary description for the list view.

        This summary is used in API documentation to give a brief description of what this view does.
        It can be overriden using the `router_kwargs`.

        Args:
            model_class (Type[Model]): The Django model class associated with this view.

        Returns:
            str: The summary description for the list view. Defaults to:
                - For `detail=False`: "List {model_name_plural}". For example, for a model "Department",
                    the summary would be "List Departments".
                - For `detail=True`: "List {related_model_name_plural} related to a {model_name}". For example,
                    for a model "Department" with a related model "Item", the summary would be
                    "List Items related to a Department".
        """
        if self.detail:
            verbose_model_name = model_class._meta.verbose_name
            verbose_related_model_name_plural = (
                self._related_model_class._meta.verbose_name_plural
            )
            return f"List {verbose_related_model_name_plural} related to a {verbose_model_name}"
        else:
            verbose_model_name_plural = model_class._meta.verbose_name_plural
            return f"List {verbose_model_name_plural}"

    def bind_to_viewset(
        self, viewset_class: Type["ModelViewSet"], model_view_name: str
    ) -> None:
        super().bind_to_viewset(viewset_class, model_view_name)
        self.bind_default_value(
            viewset_class=viewset_class,
            model_view_name=model_view_name,
            attribute_name="output_schema",
            default_attribute_name="default_output_schema",
        )
