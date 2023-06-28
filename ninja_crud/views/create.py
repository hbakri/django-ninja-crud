from http import HTTPStatus
from typing import Any, Callable, List, Type, Union

from django.db.models import Model
from django.http import HttpRequest
from ninja import Router, Schema

from ninja_crud.views import utils
from ninja_crud.views.abstract import AbstractModelView


class CreateModelView(AbstractModelView):
    def __init__(
        self,
        input_schema: Type[Schema],
        output_schema: Type[Schema],
        decorators: List[Callable] = None,
        detail: bool = False,
        related_model: Type[Model] = None,
        pre_save: Union[
            Callable[[HttpRequest, Model], None],
            Callable[[HttpRequest, Any, Model], None],
        ] = None,
        post_save: Union[
            Callable[[HttpRequest, Model], None],
            Callable[[HttpRequest, Any, Model], None],
        ] = None,
    ) -> None:
        super().__init__(decorators=decorators)
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.detail = detail
        self.related_model = related_model
        self.pre_save = pre_save
        self.post_save = post_save

    def register_route(self, router: Router, model: Type[Model]) -> None:
        if self.detail:
            self.register_instance_route(router, model)
        else:
            self.register_collection_route(router, model)

    def register_collection_route(self, router: Router, model: Type[Model]) -> None:
        model_name = utils.to_snake_case(model.__name__)
        operation_id = f"create_{model_name}"
        summary = f"Create {model.__name__}"

        input_schema = self.input_schema
        output_schema = self.output_schema

        @router.post(
            "/",
            response={HTTPStatus.CREATED: output_schema},
            url_name=self.get_url_name(model),
            operation_id=operation_id,
            summary=summary,
        )
        @utils.merge_decorators(self.decorators)
        def create_model(request: HttpRequest, payload: input_schema):
            instance = model()
            for field, value in payload.dict(exclude_unset=True).items():
                setattr(instance, field, value)
            if self.pre_save:
                self.pre_save(request, instance)
            instance.full_clean()
            instance.save()
            if self.post_save:
                self.post_save(request, instance)
            return HTTPStatus.CREATED, instance

    def register_instance_route(self, router: Router, model: Type[Model]) -> None:
        parent_model_name = utils.to_snake_case(model.__name__)
        model_name = utils.to_snake_case(self.related_model.__name__)
        plural_model_name = f"{model_name}s"
        url = "/{id}/" + plural_model_name
        operation_id = f"create_{parent_model_name}_{model_name}"
        summary = f"Create {self.related_model.__name__}"

        input_schema = self.input_schema
        output_schema = self.output_schema
        id_type = utils.get_id_type(model)

        @router.post(
            url,
            response={HTTPStatus.CREATED: output_schema},
            url_name=self.get_url_name(model),
            operation_id=operation_id,
            summary=summary,
        )
        @utils.merge_decorators(self.decorators)
        def create_model(request: HttpRequest, id: id_type, payload: input_schema):
            instance = self.related_model()
            for field, value in payload.dict(exclude_unset=True).items():
                setattr(instance, field, value)
            if self.pre_save:
                self.pre_save(request, id, instance)
            instance.full_clean()
            instance.save()
            if self.post_save:
                self.post_save(request, id, instance)
            return HTTPStatus.CREATED, instance

    def get_url_name(self, model: Type[Model]) -> str:
        model_name = utils.to_snake_case(model.__name__)
        if self.detail:
            related_model_name = utils.to_snake_case(self.related_model.__name__)
            return f"{model_name}_{related_model_name}s"
        else:
            return f"{model_name}s"
