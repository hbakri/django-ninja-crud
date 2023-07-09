from http import HTTPStatus
from typing import Any, Callable, List, Type

from django.db.models import Model, QuerySet
from django.http import HttpRequest
from ninja import Router, Schema

from ninja_crud.views import utils
from ninja_crud.views.abstract import AbstractModelView


class RetrieveModelView(AbstractModelView):
    def __init__(
        self,
        output_schema: Type[Schema],
        queryset_getter: Callable[[Any], QuerySet[Model]] = None,
        decorators: List[Callable] = None,
    ) -> None:
        super().__init__(decorators=decorators)
        self.output_schema = output_schema
        self.queryset_getter = queryset_getter

    def register_route(self, router: Router, model: Type[Model]) -> None:
        @router.get(
            path=self.get_path(),
            response=self.output_schema,
            operation_id=f"retrieve_{utils.to_snake_case(model.__name__)}",
            summary=f"Retrieve {model.__name__}",
        )
        @utils.merge_decorators(self.decorators)
        def retrieve_model(request: HttpRequest, id: utils.get_id_type(model)):
            queryset = self.get_queryset(model, id)
            instance = queryset.get(pk=id)
            return HTTPStatus.OK, instance

    def get_queryset(self, model: Type[Model], id: Any = None) -> QuerySet[Model]:
        if self.queryset_getter is None:
            return model.objects.get_queryset()
        else:
            return self.queryset_getter(id)

    def get_path(self) -> str:
        return "/{id}"
