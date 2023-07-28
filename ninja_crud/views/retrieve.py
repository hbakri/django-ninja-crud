from http import HTTPStatus
from typing import Any, Callable, List, Optional, Type

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
        router_kwargs: Optional[dict] = None,
    ) -> None:
        super().__init__(decorators=decorators)
        self.output_schema = output_schema
        self.queryset_getter = queryset_getter
        self.router_kwargs = router_kwargs or {}

    def register_route(self, router: Router, model_class: Type[Model]) -> None:
        @router.get(
            path=self.get_path(),
            response=self.output_schema,
            operation_id=f"retrieve_{utils.to_snake_case(model_class.__name__)}",
            summary=f"Retrieve {model_class.__name__}",
            **self.router_kwargs,
        )
        @utils.merge_decorators(self.decorators)
        def retrieve_model(request: HttpRequest, id: utils.get_id_type(model_class)):
            queryset = self.get_queryset(model_class, id)
            instance = queryset.get(pk=id)
            return HTTPStatus.OK, instance

    def get_queryset(self, model_class: Type[Model], id: Any = None) -> QuerySet[Model]:
        if self.queryset_getter is None:
            return model_class.objects.get_queryset()
        else:
            return self.queryset_getter(id)

    def get_path(self) -> str:
        return "/{id}"
