from http import HTTPStatus
from typing import Callable, List, Type
from uuid import UUID

from django.db.models import Model
from django.http import HttpRequest
from ninja import Router

from ninja_crud import utils
from ninja_crud.utils import merge_decorators
from ninja_crud.views.abstract import AbstractModelView


class DeleteModelView(AbstractModelView):
    def __init__(
        self,
        decorators: List[Callable] = None,
        pre_delete: Callable[[HttpRequest, Model], None] = None,
        post_delete: Callable[[HttpRequest, int | UUID], None] = None,
    ) -> None:
        super().__init__(decorators=decorators)
        self.pre_delete = pre_delete
        self.post_delete = post_delete

    def register_route(self, router: Router, model: Type[Model]) -> None:
        model_name = utils.to_snake_case(model.__name__)
        operation_id = f"delete_{model_name}"
        summary = f"Delete {model.__name__}"

        @router.delete(
            "/{id}",
            response={HTTPStatus.NO_CONTENT: None},
            url_name=model_name,
            operation_id=operation_id,
            summary=summary,
        )
        @merge_decorators(self.decorators)
        def delete_model(request: HttpRequest, id: int | UUID):
            instance = model.objects.get(pk=id)
            if self.pre_delete is not None:
                self.pre_delete(request, instance)
            instance.delete()
            if self.post_delete is not None:
                self.post_delete(request, id)
            return HTTPStatus.NO_CONTENT, None
