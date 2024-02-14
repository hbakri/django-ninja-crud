import http
from typing import Callable, Dict, List, Optional, Type

import django.db.models
import ninja
from django.http import HttpRequest

from ninja_crud.views.abstract_model_view import AbstractModelView
from ninja_crud.views.enums import HTTPMethod


class CreateModelView(AbstractModelView):
    def __init__(
        self,
        path: str = "/",
        path_parameters: Optional[ninja.Schema] = None,
        request_body: Optional[Type[ninja.Schema]] = None,
        response_body: Optional[Type[ninja.Schema]] = None,
        create_model: Optional[
            Callable[[Optional[ninja.Schema]], django.db.models.Model]
        ] = None,
        pre_save: Optional[
            Callable[[HttpRequest, django.db.models.Model], None]
        ] = None,
        post_save: Optional[
            Callable[[HttpRequest, django.db.models.Model], None]
        ] = None,
        decorators: Optional[List[Callable]] = None,
        router_kwargs: Optional[Dict] = None,
    ) -> None:
        super().__init__(
            method=HTTPMethod.POST,
            path=path,
            path_parameters=path_parameters,
            query_parameters=None,
            request_body=request_body,
            response_body=response_body,
            response_status=http.HTTPStatus.CREATED,
            decorators=decorators,
            router_kwargs=router_kwargs,
        )
        self.create_model = create_model or self.default_create_model
        self.pre_save = pre_save
        self.post_save = post_save

    def default_create_model(
        self,
        path_parameters: Optional[ninja.Schema],
    ) -> django.db.models.Model:
        return self.model_viewset_class.model()

    # TODO: add path_parameters to the signature of hooks and the same stuff as
    # RUD views

    def handle_request(
        self,
        request: HttpRequest,
        path_parameters: Optional[ninja.Schema],
        query_parameters: Optional[ninja.Schema],
        request_body: Optional[ninja.Schema],
    ) -> django.db.models.Model:
        if path_parameters:
            self.model_viewset_class.model.objects.get(**path_parameters.dict())

        instance = self.create_model(path_parameters)

        if request_body:
            for field, value in request_body.dict().items():
                setattr(instance, field, value)

        if self.pre_save:
            self.pre_save(request, instance)

        instance.full_clean()
        instance.save()

        if self.post_save:
            self.post_save(request, instance)

        return instance

    def _inherit_model_viewset_class_attributes(self) -> None:
        if self.request_body is None:
            self.request_body = self.model_viewset_class.default_request_body
        if self.response_body is None:
            self.response_body = self.model_viewset_class.default_response_body
