import http
from typing import Callable, Dict, List, Optional, Type

import django.db.models
import django.http
import ninja
import ninja.pagination

from ninja_crud.views.abstract_model_view import AbstractModelView
from ninja_crud.views.enums import HTTPMethod


class ListModelView(AbstractModelView):
    def __init__(
        self,
        path: str = "/",
        path_parameters: Optional[Type[ninja.Schema]] = None,
        query_parameters: Optional[Type[ninja.Schema]] = None,
        response_body: Optional[Type[List[ninja.Schema]]] = None,
        get_queryset: Optional[
            Callable[[Optional[ninja.Schema]], django.db.models.QuerySet]
        ] = None,
        pagination_class: Optional[
            Type[ninja.pagination.PaginationBase]
        ] = ninja.pagination.LimitOffsetPagination,
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
            self.decorators.append(ninja.pagination.paginate(self.pagination_class))

    def default_get_queryset(
        self,
        path_parameters: Optional[ninja.Schema],
    ) -> django.db.models.QuerySet:
        return self.model_viewset_class.model.objects.get_queryset()

    @staticmethod
    def filter_queryset(
        queryset: django.db.models.QuerySet,
        query_parameters: Optional[ninja.Schema],
    ) -> django.db.models.QuerySet:
        if query_parameters:
            if isinstance(query_parameters, ninja.FilterSchema):
                queryset = query_parameters.filter(queryset)
            else:
                queryset = queryset.filter(**query_parameters.dict(exclude_unset=True))
        return queryset

    def handle_request(
        self,
        request: django.http.HttpRequest,
        path_parameters: Optional[ninja.Schema],
        query_parameters: Optional[ninja.Schema],
        request_body: Optional[ninja.Schema],
    ) -> django.db.models.QuerySet:
        if path_parameters:
            self.model_viewset_class.model.objects.get(**path_parameters.dict())

        queryset = self.get_queryset(path_parameters)
        queryset = self.filter_queryset(queryset, query_parameters)

        return queryset

    def _inherit_model_viewset_class_attributes(self) -> None:
        if self.response_body is None:
            self.response_body = List[self.model_viewset_class.default_response_body]
