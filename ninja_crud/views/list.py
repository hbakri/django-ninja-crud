from http import HTTPStatus
from typing import Callable, List, Type, Union
from uuid import UUID

from django.db.models import Model, QuerySet
from django.http import HttpRequest
from ninja import FilterSchema, Query, Router, Schema
from ninja.pagination import LimitOffsetPagination, paginate

from ninja_crud import utils
from ninja_crud.utils import merge_decorators
from ninja_crud.views.abstract import AbstractModelView


class ListModelView(AbstractModelView):
    def __init__(
        self,
        output_schema: Type[Schema],
        filter_schema: Type[FilterSchema] = None,
        queryset_getter: Union[
            Callable[[], QuerySet[Model]], Callable[[UUID], QuerySet[Model]]
        ] = None,
        related_model: Type[Model] = None,
        detail: bool = False,
        decorators: List[Callable] = None,
    ) -> None:
        super().__init__(decorators=decorators)
        self.output_schema = output_schema
        self.filter_schema = filter_schema
        self.get_queryset = queryset_getter
        self.related_model = related_model
        self.detail = detail

    def register_route(self, router: Router, model: Type[Model]) -> None:
        if self.detail:
            self.register_instance_route(router, model)
        else:
            self.register_collection_route(router, model)

    def register_collection_route(self, router: Router, model: Type[Model]) -> None:
        model_name = utils.to_snake_case(model.__name__)
        operation_id = f"list_{model_name}s"
        summary = f"List {model.__name__}s"

        output_schema = self.output_schema
        filter_schema = self.filter_schema

        @router.get(
            "/",
            response={HTTPStatus.OK: List[output_schema]},
            url_name=f"{model_name}s",
            operation_id=operation_id,
            summary=summary,
        )
        @merge_decorators(self.decorators)
        @paginate(LimitOffsetPagination)
        def list_models(
            request: HttpRequest, filters: filter_schema = Query(default=FilterSchema())
        ):
            if self.get_queryset is not None:
                queryset = self.get_queryset()
            else:
                queryset = model.objects.get_queryset()
            return self.filter_queryset(queryset=queryset, filters=filters)

    def register_instance_route(self, router: Router, model: Type[Model]) -> None:
        parent_model_name = utils.to_snake_case(model.__name__)
        model_name = utils.to_snake_case(self.related_model.__name__)
        plural_model_name = f"{model_name}s"
        url = "/{id}/" + plural_model_name
        operation_id = f"list_{parent_model_name}_{plural_model_name}"
        summary = f"List {self.related_model.__name__}s of a {model.__name__}"

        output_schema = self.output_schema
        filter_schema = self.filter_schema

        @router.get(
            url,
            response={HTTPStatus.OK: List[output_schema]},
            url_name=f"{parent_model_name}_{plural_model_name}",
            operation_id=operation_id,
            summary=summary,
        )
        @merge_decorators(self.decorators)
        @paginate(LimitOffsetPagination)
        def list_models(
            request: HttpRequest,
            id: UUID,
            filters: filter_schema = Query(default=FilterSchema()),
        ):
            if self.get_queryset is not None:
                queryset = self.get_queryset(id)
            else:
                queryset = self.related_model.objects.get_queryset()
            return self.filter_queryset(queryset=queryset, filters=filters)

    @staticmethod
    def filter_queryset(queryset: QuerySet[Model], filters: FilterSchema):
        filters_dict = filters.dict()
        if "order_by" in filters_dict and filters_dict["order_by"] is not None:
            queryset = queryset.order_by(*filters_dict.pop("order_by"))

        queryset = filters.filter(queryset)
        return queryset
