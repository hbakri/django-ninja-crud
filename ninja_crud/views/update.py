from http import HTTPStatus
from typing import Callable, List, Type

from django.db.models import Model
from django.http import HttpRequest
from ninja import Router, Schema

from ninja_crud.views import utils
from ninja_crud.views.abstract import AbstractModelView


class UpdateModelView(AbstractModelView):
    def __init__(
        self,
        input_schema: Type[Schema],
        output_schema: Type[Schema],
        decorators: List[Callable] = None,
        pre_save: Callable[[HttpRequest, Model], None] = None,
        post_save: Callable[[HttpRequest, Model], None] = None,
    ) -> None:
        super().__init__(decorators=decorators)
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.pre_save = pre_save
        self.post_save = post_save

    def register_route(self, router: Router, model: Type[Model]) -> None:
        model_name = utils.to_snake_case(model.__name__)
        operation_id = f"update_{model_name}"
        summary = f"Update {model.__name__}"

        input_schema = self.input_schema
        output_schema = self.output_schema
        id_type = utils.get_id_type(model)

        @router.put(
            "/{id}",
            response={HTTPStatus.OK: output_schema},
            url_name=self.get_url_name(model),
            operation_id=operation_id,
            summary=summary,
        )
        @utils.merge_decorators(self.decorators)
        def update_model(request: HttpRequest, id: id_type, payload: input_schema):
            instance = model.objects.get(id=id)
            for field, value in payload.dict(exclude_unset=True).items():
                setattr(instance, field, value)
            if self.pre_save is not None:
                self.pre_save(request, instance)
            instance.full_clean()
            instance.save()
            if self.post_save is not None:
                self.post_save(request, instance)
            return HTTPStatus.OK, instance

    @staticmethod
    def get_url_name(model: Type[Model]) -> str:
        return utils.to_snake_case(model.__name__)
