import copy
from http import HTTPStatus
from typing import Callable, List, Type, TypeVar

from django.db.models import Model
from django.http import HttpRequest
from ninja import Router, Schema

from ninja_crud.views import utils
from ninja_crud.views.abstract import AbstractModelView

ModelType = TypeVar("ModelType", bound=Model)
PreSaveHook = Callable[[HttpRequest, ModelType, ModelType], None]
PostSaveHook = Callable[[HttpRequest, ModelType, ModelType], None]


class UpdateModelView(AbstractModelView):
    def __init__(
        self,
        input_schema: Type[Schema],
        output_schema: Type[Schema],
        decorators: List[Callable] = None,
        pre_save: PreSaveHook = None,
        post_save: PostSaveHook = None,
    ) -> None:
        super().__init__(decorators=decorators)
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.pre_save = pre_save
        self.post_save = post_save
        self.http_method = "PUT"

    def register_route(self, router: Router, model_class: Type[Model]) -> None:
        input_schema = self.input_schema
        output_schema = self.output_schema

        @router.api_operation(
            methods=[self.http_method],
            path=self.get_path(),
            response={HTTPStatus.OK: output_schema},
            operation_id=f"update_{utils.to_snake_case(model_class.__name__)}",
            summary=f"Update {model_class.__name__}",
        )
        @utils.merge_decorators(self.decorators)
        def update_model(
            request: HttpRequest,
            id: utils.get_id_type(model_class),
            payload: input_schema,
        ):
            instance = model_class.objects.get(pk=id)

            old_instance = None
            if self.pre_save is not None or self.post_save is not None:
                old_instance = copy.deepcopy(instance)

            for field, value in payload.dict(exclude_unset=True).items():
                setattr(instance, field, value)

            if self.pre_save is not None:
                self.pre_save(request, instance, old_instance)

            instance.full_clean()
            instance.save()

            if self.post_save is not None:
                self.post_save(request, instance, old_instance)

            return HTTPStatus.OK, instance

    def get_path(self) -> str:
        return "/{id}"
