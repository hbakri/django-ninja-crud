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
        self.get_queryset = queryset_getter

    def register_route(self, router: Router, model: Type[Model]) -> None:
        model_name = utils.to_snake_case(model.__name__)
        operation_id = f"retrieve_{model_name}"
        summary = f"Retrieve {model.__name__}"

        output_schema = self.output_schema
        id_type = utils.get_id_type(model)

        @router.get(
            "/{id}",
            response={HTTPStatus.OK: output_schema},
            url_name=model_name,
            operation_id=operation_id,
            summary=summary,
        )
        @utils.merge_decorators(self.decorators)
        def retrieve_model(request: HttpRequest, id: id_type):
            if self.get_queryset is not None:
                queryset = self.get_queryset(id)
            else:
                queryset = model.objects.get_queryset()
            instance = queryset.get(id=id)
            return HTTPStatus.OK, instance
