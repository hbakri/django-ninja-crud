import functools
from http import HTTPStatus
from typing import Any, Callable, List, Optional, Type, Union

from django.db.models import Model, QuerySet
from django.http import HttpRequest
from ninja import FilterSchema, Query, Router, Schema
from ninja.pagination import LimitOffsetPagination, paginate

from ninja_crud.views import utils
from ninja_crud.views.abstract import AbstractModelView
from ninja_crud.views.enums import HTTPMethod
from ninja_crud.views.types import CollectionQuerySetGetter, DetailQuerySetGetter
from ninja_crud.views.validators.queryset_getter_validator import (
    QuerySetGetterValidator,
)


class ListModelView(AbstractModelView):
    """
    A view class that handles listing instances of a model.
    It allows customization through a queryset getter and also supports decorators.

    Example:
    ```python
    from ninja_crud.views import ModelViewSet, ListModelView
    from example.models import Department, Employee
    from example.schemas import DepartmentOut, EmployeeOut

    class DepartmentViewSet(ModelViewSet):
        model_class = Department

        # Basic usage: List all departments
        # GET /departments/
        list = ListModelView(output_schema=DepartmentOut)

        # Advanced usage: List employees of a specific department
        # GET /departments/{id}/employees/
        list_employees = ListModelView(
            detail=True,
            queryset_getter=lambda id: Employee.objects.filter(department_id=id),
            output_schema=EmployeeOut,
        )
    ```
    """

    def __init__(
        self,
        output_schema: Type[Schema],
        filter_schema: Optional[Type[FilterSchema]] = None,
        detail: bool = False,
        queryset_getter: Union[
            DetailQuerySetGetter, CollectionQuerySetGetter, None
        ] = None,
        path: Optional[str] = None,
        decorators: Optional[List[Callable]] = None,
        pagination_decorator: Optional[Callable] = paginate(LimitOffsetPagination),
        router_kwargs: Optional[dict] = None,
    ) -> None:
        """
        Initializes the ListModelView.

        Args:
            output_schema (Type[Schema]): The schema used to serialize the retrieved objects.
            filter_schema (Type[FilterSchema], optional): The schema used to validate the filters.
            detail (bool, optional): Whether the view is a detail or collection view. Defaults to False.

                If set to True, `queryset_getter` must be provided.
            queryset_getter (Union[DetailQuerySetGetter, CollectionQuerySetGetter], optional): A
                function to customize the queryset used for retrieving the objects. Defaults to None.
                The function should have one of the following signatures:
                - For `detail=False`: () -> QuerySet[Model]
                - For `detail=True`: (id: Any) -> QuerySet[Model]

                If not provided, the default manager of the `model_class` specified in the
                `ModelViewSet` will be used.
            path (str, optional): The path to use for the view. Defaults to:
                - For `detail=False`: "/"
                - For `detail=True`: "/{id}/{related_model_name_plural_to_snake_case}/"

                Where `related_model_name_plural_to_snake_case` refers to the plural form of the related model's name,
                converted to snake_case. For example, for a related model "ItemDetail", the path might look like
                "/{id}/item_details/".
            decorators (List[Callable], optional): A list of decorators to apply to the view. Defaults to [].
            pagination_decorator (Callable, optional): A decorator to apply to the view for pagination. Defaults to
                `ninja.pagination.paginate(LimitOffsetPagination)`.
            router_kwargs (dict, optional): Additional arguments to pass to the router. Defaults to {}.
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
        self.pagination_decorator = pagination_decorator
        if pagination_decorator is not None:
            decorators = decorators or []
            decorators.append(pagination_decorator)
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
        self._related_model = queryset_getter_model_class

    def register_route(self, router: Router, model_class: Type[Model]) -> None:
        if self.detail:
            self._register_detail_route(router, model_class)
        else:
            self._register_collection_route(router, model_class)

    def _register_detail_route(self, router: Router, model_class: Type[Model]) -> None:
        filter_schema = self.filter_schema

        @self._configure_route(router, model_class)
        def list_models(
            request: HttpRequest,
            id: utils.get_id_type(model_class),
            filters: filter_schema = Query(default=FilterSchema()),
        ):
            if not model_class.objects.filter(pk=id).exists():
                raise model_class.DoesNotExist(
                    f"{model_class.__name__} with pk '{id}' does not exist."
                )

            queryset = self._get_queryset(model_class, id)
            return self._filter_queryset(queryset=queryset, filters=filters)

    def _register_collection_route(
        self, router: Router, model_class: Type[Model]
    ) -> None:
        filter_schema = self.filter_schema

        @self._configure_route(router, model_class)
        def list_models(
            request: HttpRequest, filters: filter_schema = Query(default=FilterSchema())
        ):
            queryset = self._get_queryset(model_class)
            return self._filter_queryset(queryset=queryset, filters=filters)

    def _configure_route(self, router: Router, model_class: Type[Model]):
        def decorator(route_func):
            @router.api_operation(
                **self._sanitize_and_merge_router_kwargs(
                    default_router_kwargs=self._get_default_router_kwargs(model_class),
                    custom_router_kwargs=self.router_kwargs,
                )
            )
            @utils.merge_decorators(self.decorators)
            @functools.wraps(route_func)
            def wrapped_func(*args, **kwargs):
                return route_func(*args, **kwargs)

            return wrapped_func

        return decorator

    def _get_queryset(
        self, model_class: Type[Model], id: Optional[Any] = None
    ) -> QuerySet[Model]:
        if self.queryset_getter:
            args = [id] if self.detail else []
            return self.queryset_getter(*args)
        else:
            return model_class.objects.get_queryset()

    @staticmethod
    def _filter_queryset(queryset: QuerySet[Model], filters: FilterSchema):
        filters_dict = filters.dict()
        if "order_by" in filters_dict and filters_dict["order_by"] is not None:
            queryset = queryset.order_by(*filters_dict.pop("order_by"))

        queryset = filters.filter(queryset)
        return queryset

    @staticmethod
    def _get_default_path(detail: bool, model_class: Type[Model]) -> str:
        if detail:
            related_model_name = utils.to_snake_case(model_class.__name__)
            return f"/{{id}}/{related_model_name}s/"
        else:
            return "/"

    def _get_default_router_kwargs(self, model_class: Type[Model]) -> dict:
        return dict(
            methods=[self.method.value],
            path=self.path,
            response={HTTPStatus.OK: List[self.output_schema]},
            operation_id=self._get_operation_id(model_class),
            summary=self._get_summary(model_class),
        )

    def _get_operation_id(self, model_class: Type[Model]) -> str:
        model_name = utils.to_snake_case(model_class.__name__)
        if self.detail:
            related_model_name = utils.to_snake_case(self._related_model.__name__)
            return f"list_{model_name}_{related_model_name}s"
        else:
            return f"list_{model_name}s"

    def _get_summary(self, model_class: Type[Model]) -> str:
        if self.detail:
            verbose_model_name = model_class._meta.verbose_name
            verbose_related_model_name_plural = (
                self._related_model._meta.verbose_name_plural
            )
            return f"List {verbose_related_model_name_plural} related to a {verbose_model_name}"
        else:
            verbose_model_name_plural = model_class._meta.verbose_name_plural
            return f"List {verbose_model_name_plural}"
