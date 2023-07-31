from http import HTTPStatus
from typing import Any, Callable, List, Optional, Type, TypeVar, Union

from django.db.models import Model
from django.http import HttpRequest
from ninja import Router, Schema

from ninja_crud.views import utils
from ninja_crud.views.abstract import AbstractModelView

ModelType = TypeVar("ModelType", bound=Model)
SaveHook = Union[
    Callable[[HttpRequest, ModelType], None],
    Callable[[HttpRequest, Any, ModelType], None],
]
PreSaveHook = SaveHook[ModelType]
PostSaveHook = SaveHook[ModelType]


class CreateModelView(AbstractModelView):
    def __init__(
        self,
        input_schema: Type[Schema],
        output_schema: Type[Schema],
        decorators: List[Callable] = None,
        detail: bool = False,
        related_model: Type[Model] = None,
        pre_save: PreSaveHook = None,
        post_save: PostSaveHook = None,
        router_kwargs: Optional[dict] = None,
    ) -> None:
        super().__init__(decorators=decorators, router_kwargs=router_kwargs)
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.detail = detail
        self.related_model = related_model
        self.pre_save = pre_save
        self.post_save = post_save

    def register_route(self, router: Router, model_class: Type[Model]) -> None:
        if self.detail:
            self.register_instance_route(router, model_class)
        else:
            self.register_collection_route(router, model_class)

    def register_collection_route(self, router: Router, model_class: Type[Model]) -> None:
        model_name = utils.to_snake_case(model_class.__name__)
        operation_id = f"create_{model_name}"

        input_schema = self.input_schema
        output_schema = self.output_schema

        @router.post(
            path=self.get_path(),
            response={HTTPStatus.CREATED: output_schema},
            operation_id=operation_id,
            summary=f"Create {model_class.__name__}",
            **self.router_kwargs,
        )
        @utils.merge_decorators(self.decorators)
        def create_model(request: HttpRequest, payload: input_schema):
            instance = model_class()
            for field, value in payload.dict(exclude_unset=True).items():
                setattr(instance, field, value)

            if self.pre_save:
                self.pre_save(request, instance)

            instance.full_clean()
            instance.save()

            if self.post_save:
                self.post_save(request, instance)

            return HTTPStatus.CREATED, instance

    def register_instance_route(self, router: Router, model_class: Type[Model]) -> None:
        parent_model_name = utils.to_snake_case(model_class.__name__)
        model_name = utils.to_snake_case(self.related_model.__name__)
        operation_id = f"create_{parent_model_name}_{model_name}"

        input_schema = self.input_schema
        output_schema = self.output_schema

        @router.post(
            path=self.get_path(),
            response={HTTPStatus.CREATED: output_schema},
            operation_id=operation_id,
            summary=f"Create {self.related_model.__name__}",
            **self.router_kwargs,
        )
        @utils.merge_decorators(self.decorators)
        def create_model(
            request: HttpRequest, id: utils.get_id_type(model_class), payload: input_schema
        ):
            instance = model_class.objects.get(pk=id)
            related_instance = self.related_model()
            for field, value in payload.dict(exclude_unset=True).items():
                setattr(related_instance, field, value)

            if self.pre_save:
                self.pre_save(request, instance.pk, related_instance)

            related_instance.full_clean()
            related_instance.save()

            if self.post_save:
                self.post_save(request, instance.pk, related_instance)

            return HTTPStatus.CREATED, related_instance

    def get_path(self) -> str:
        if self.detail:
            return f"/{{id}}/{utils.to_snake_case(self.related_model.__name__)}s/"
        else:
            return "/"
