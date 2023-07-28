from http import HTTPStatus
from typing import Any, Callable, List, Optional, Type, Union

from django.db.models import Model, QuerySet
from django.http import HttpRequest
from ninja import FilterSchema, Query, Router, Schema
from ninja.pagination import LimitOffsetPagination, paginate

from ninja_crud.views import utils
from ninja_crud.views.abstract import AbstractModelView


class ListModelView(AbstractModelView):
    def __init__(
        self,
        output_schema: Type[Schema],
        filter_schema: Type[FilterSchema] = None,
        queryset_getter: Union[
            Callable[[], QuerySet[Model]], Callable[[Any], QuerySet[Model]]
        ] = None,
        related_model: Type[Model] = None,
        detail: bool = False,
        decorators: List[Callable] = None,
        router_kwargs: Optional[dict] = None,
    ) -> None:
        super().__init__(decorators=decorators)
        self.output_schema = output_schema
        self.filter_schema = filter_schema
        self.queryset_getter = queryset_getter
        self.related_model = related_model
        self.detail = detail
        self.router_kwargs = router_kwargs or {}

    def register_route(self, router: Router, model_class: Type[Model]) -> None:
        if self.detail:
            self.register_instance_route(router, model_class)
        else:
            self.register_collection_route(router, model_class)

    def register_collection_route(self, router: Router, model_class: Type[Model]) -> None:
        model_name = utils.to_snake_case(model_class.__name__)
        operation_id = f"list_{model_name}s"
        summary = f"List {model_class.__name__}s"

        output_schema = self.output_schema
        filter_schema = self.filter_schema

        @router.get(
            path=self.get_path(),
            response={HTTPStatus.OK: List[output_schema]},
            operation_id=operation_id,
            summary=summary,
            **self.router_kwargs,
        )
        @utils.merge_decorators(self.decorators)
        @paginate(LimitOffsetPagination)
        def list_models(
            request: HttpRequest, filters: filter_schema = Query(default=FilterSchema())
        ):
            queryset = self.get_queryset(model_class)
            return self.filter_queryset(queryset=queryset, filters=filters)

    def register_instance_route(self, router: Router, model_class: Type[Model]) -> None:
        parent_model_name = utils.to_snake_case(model_class.__name__)
        related_model_name = utils.to_snake_case(self.related_model.__name__)
        operation_id = f"list_{parent_model_name}_{related_model_name}s"
        summary = f"List {self.related_model.__name__}s of a {model_class.__name__}"

        output_schema = self.output_schema
        filter_schema = self.filter_schema

        @router.get(
            path=self.get_path(),
            response={HTTPStatus.OK: List[output_schema]},
            operation_id=operation_id,
            summary=summary,
            **self.router_kwargs,
        )
        @utils.merge_decorators(self.decorators)
        @paginate(LimitOffsetPagination)
        def list_models(
            request: HttpRequest,
            id: utils.get_id_type(model_class),
            filters: filter_schema = Query(default=FilterSchema()),
        ):
            instance = model_class.objects.get(pk=id)
            queryset = self.get_queryset(model_class, instance.pk)
            return self.filter_queryset(queryset=queryset, filters=filters)

    def get_queryset(self, model_class: Type[Model], id: Any = None) -> QuerySet[Model]:
        if self.detail:
            if self.queryset_getter is not None:
                return self.queryset_getter(id)
            else:
                return self.related_model.objects.get_queryset()
        else:
            if self.queryset_getter is not None:
                return self.queryset_getter()
            else:
                return model_class.objects.get_queryset()

    @staticmethod
    def filter_queryset(queryset: QuerySet[Model], filters: FilterSchema):
        filters_dict = filters.dict()
        if "order_by" in filters_dict and filters_dict["order_by"] is not None:
            queryset = queryset.order_by(*filters_dict.pop("order_by"))

        queryset = filters.filter(queryset)
        return queryset

    def get_path(self) -> str:
        if self.detail:
            return f"/{{id}}/{utils.to_snake_case(self.related_model.__name__)}s/"
        else:
            return "/"
