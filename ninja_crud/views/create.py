import functools
from http import HTTPStatus
from typing import Any, Callable, List, Optional, Type, Union

from django.db.models import Model
from django.http import HttpRequest
from ninja import Router, Schema

from ninja_crud.views import utils
from ninja_crud.views.abstract import AbstractModelView
from ninja_crud.views.types import CreateCollectionSaveHook, CreateDetailSaveHook


class CreateModelView(AbstractModelView):
    def __init__(
        self,
        input_schema: Type[Schema],
        output_schema: Type[Schema],
        decorators: List[Callable] = None,
        detail: bool = False,
        related_model: Type[Model] = None,
        pre_save: Union[CreateDetailSaveHook, CreateCollectionSaveHook] = None,
        post_save: Union[CreateDetailSaveHook, CreateCollectionSaveHook] = None,
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
            self._register_detail_route(router, model_class)
        else:
            self._register_collection_route(router, model_class)

    def _register_detail_route(self, router: Router, model_class: Type[Model]) -> None:
        input_schema = self.input_schema

        @self._configure_route(router, model_class)
        def create_model(
            request: HttpRequest,
            id: utils.get_id_type(model_class),
            payload: input_schema,
        ):
            if not model_class.objects.filter(pk=id).exists():
                raise model_class.DoesNotExist(
                    f"{model_class.__name__} with ID '{id}' does not exist."
                )

            instance = self.related_model()
            instance = self._save_model(instance, payload, request, id=id)
            return HTTPStatus.CREATED, instance

    def _register_collection_route(
        self, router: Router, model_class: Type[Model]
    ) -> None:
        input_schema = self.input_schema

        @self._configure_route(router, model_class)
        def create_model(request: HttpRequest, payload: input_schema):
            instance = model_class()
            instance = self._save_model(instance, payload, request)
            return HTTPStatus.CREATED, instance

    def get_path(self) -> str:
        if self.detail:
            related_model_name = utils.to_snake_case(self.related_model.__name__)
            return f"/{{id}}/{related_model_name}s/"
        else:
            return "/"

    def _save_model(
        self, instance: Model, payload: Schema, request: HttpRequest, id: Any = None
    ) -> Model:
        for field, value in payload.dict(exclude_unset=True).items():
            setattr(instance, field, value)

        if self.pre_save:
            args = (request, instance) if not id else (request, id, instance)
            self.pre_save(*args)

        instance.full_clean()
        instance.save()

        if self.post_save:
            args = (request, instance) if not id else (request, id, instance)
            self.post_save(*args)

        return instance

    def _configure_route(self, router: Router, model_class: Type[Model]):
        def decorator(route_func):
            @router.post(
                path=self.get_path(),
                response={HTTPStatus.CREATED: self.output_schema},
                operation_id=self._get_operation_id(model_class),
                summary=self._get_summary(model_class),
                **self.router_kwargs,
            )
            @utils.merge_decorators(self.decorators)
            @functools.wraps(route_func)
            def wrapped_func(*args, **kwargs):
                return route_func(*args, **kwargs)

            return wrapped_func

        return decorator

    def _get_operation_id(self, model_class: Type[Model]) -> str:
        model_name = utils.to_snake_case(model_class.__name__)
        if self.detail:
            related_model_name = utils.to_snake_case(self.related_model.__name__)
            return f"create_{model_name}_{related_model_name}"
        else:
            return f"create_{model_name}"

    def _get_summary(self, model_class: Type[Model]) -> str:
        verbose_model_name = model_class._meta.verbose_name
        if self.detail:
            verbose_model_name = model_class._meta.verbose_name
            verbose_related_model_name = self.related_model._meta.verbose_name
            return f"Create {verbose_related_model_name} for {verbose_model_name}"
        else:
            return f"Create {verbose_model_name}"
