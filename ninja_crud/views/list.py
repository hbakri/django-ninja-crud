import functools
from http import HTTPStatus
from typing import Any, Callable, List, Optional, Type, Union

from django.db.models import Model, QuerySet
from django.http import HttpRequest
from ninja import FilterSchema, Query, Router, Schema
from ninja.pagination import LimitOffsetPagination, paginate

from ninja_crud.views import utils
from ninja_crud.views.abstract import AbstractModelView
from ninja_crud.views.types import CollectionQuerySetGetter, DetailQuerySetGetter
from ninja_crud.views.validators.queryset_getter_validator import (
    QuerySetGetterValidator,
)


class ListModelView(AbstractModelView):
    def __init__(
        self,
        output_schema: Type[Schema],
        filter_schema: Type[FilterSchema] = None,
        queryset_getter: Union[DetailQuerySetGetter, CollectionQuerySetGetter] = None,
        detail: bool = False,
        decorators: List[Callable] = None,
        router_kwargs: Optional[dict] = None,
    ) -> None:
        super().__init__(decorators=decorators, router_kwargs=router_kwargs)
        self.output_schema = output_schema
        self.filter_schema = filter_schema
        self.queryset_getter = queryset_getter
        self.detail = detail

        QuerySetGetterValidator.validate(queryset_getter, detail)
        self._related_model = queryset_getter(None).model if detail else None

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
                    f"{model_class.__name__} with ID '{id}' does not exist."
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

    def get_path(self) -> str:
        if self.detail:
            related_model_name = utils.to_snake_case(self._related_model.__name__)
            return f"/{{id}}/{related_model_name}s/"
        else:
            return "/"

    def _configure_route(self, router: Router, model_class: Type[Model]):
        def decorator(route_func):
            @router.get(
                path=self.get_path(),
                response={HTTPStatus.OK: List[self.output_schema]},
                operation_id=self._get_operation_id(model_class),
                summary=self._get_summary(model_class),
                **self.router_kwargs,
            )
            @utils.merge_decorators(self.decorators)
            @paginate(LimitOffsetPagination)
            @functools.wraps(route_func)
            def wrapped_func(*args, **kwargs):
                return route_func(*args, **kwargs)

            return wrapped_func

        return decorator

    def _get_queryset(
        self, model_class: Type[Model], id: Any = None
    ) -> QuerySet[Model]:
        if self.queryset_getter:
            if self.detail:
                return self.queryset_getter(id)
            else:
                return self.queryset_getter()
        else:
            return model_class.objects.get_queryset()

    @staticmethod
    def _filter_queryset(queryset: QuerySet[Model], filters: FilterSchema):
        filters_dict = filters.dict()
        if "order_by" in filters_dict and filters_dict["order_by"] is not None:
            queryset = queryset.order_by(*filters_dict.pop("order_by"))

        queryset = filters.filter(queryset)
        return queryset

    def _get_operation_id(self, model_class: Type[Model]) -> str:
        model_name = utils.to_snake_case(model_class.__name__)
        if self.detail:
            related_model_name = utils.to_snake_case(self._related_model.__name__)
            return f"list_{model_name}_{related_model_name}s"
        else:
            return f"list_{model_name}s"

    def _get_summary(self, model_class: Type[Model]) -> str:
        model_name = model_class.__name__
        if self.detail:
            related_model_name = self._related_model.__name__
            return f"List {related_model_name}s related to a {model_name}"
        else:
            return f"List {model_name}s"
