from http import HTTPStatus
from typing import Any, Callable, List, Type, TypeVar

from django.db.models import Model
from django.http import HttpRequest
from ninja import Router

from ninja_crud.views import utils
from ninja_crud.views.abstract import AbstractModelView

ModelType = TypeVar("ModelType", bound=Model)
PreDeleteHook = Callable[[HttpRequest, ModelType], None]
PostDeleteHook = Callable[[HttpRequest, Any], None]


class DeleteModelView(AbstractModelView):
    def __init__(
        self,
        decorators: List[Callable] = None,
        pre_delete: PreDeleteHook = None,
        post_delete: PostDeleteHook = None,
    ) -> None:
        super().__init__(decorators=decorators)
        self.pre_delete = pre_delete
        self.post_delete = post_delete

    def register_route(self, router: Router, model_class: Type[Model]) -> None:
        @router.delete(
            path=self.get_path(),
            response={HTTPStatus.NO_CONTENT: None},
            operation_id=f"delete_{utils.to_snake_case(model_class.__name__)}",
            summary=f"Delete {model_class.__name__}",
        )
        @utils.merge_decorators(self.decorators)
        def delete_model(request: HttpRequest, id: utils.get_id_type(model_class)):
            instance = model_class.objects.get(pk=id)

            if self.pre_delete is not None:
                self.pre_delete(request, instance)

            instance.delete()

            if self.post_delete is not None:
                self.post_delete(request, id)

            return HTTPStatus.NO_CONTENT, None

    def get_path(self) -> str:
        return "/{id}"
