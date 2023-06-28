from http import HTTPStatus
from typing import Any, Callable, List, Type

from django.db.models import Model
from django.http import HttpRequest
from ninja import Router

from ninja_crud.views import utils
from ninja_crud.views.abstract import AbstractModelView


class DeleteModelView(AbstractModelView):
    def __init__(
        self,
        decorators: List[Callable] = None,
        pre_delete: Callable[[HttpRequest, Model], None] = None,
        post_delete: Callable[[HttpRequest, Any], None] = None,
    ) -> None:
        super().__init__(decorators=decorators)
        self.pre_delete = pre_delete
        self.post_delete = post_delete

    def register_route(self, router: Router, model: Type[Model]) -> None:
        model_name = utils.to_snake_case(model.__name__)
        operation_id = f"delete_{model_name}"
        summary = f"Delete {model.__name__}"
        id_type = utils.get_id_type(model)

        @router.delete(
            "/{id}",
            response={HTTPStatus.NO_CONTENT: None},
            url_name=self.get_url_name(model),
            operation_id=operation_id,
            summary=summary,
        )
        @utils.merge_decorators(self.decorators)
        def delete_model(request: HttpRequest, id: id_type):
            instance = model.objects.get(id=id)
            if self.pre_delete is not None:
                self.pre_delete(request, instance)
            instance.delete()
            if self.post_delete is not None:
                self.post_delete(request, id)
            return HTTPStatus.NO_CONTENT, None

    @staticmethod
    def get_url_name(model: Type[Model]) -> str:
        return utils.to_snake_case(model.__name__)
