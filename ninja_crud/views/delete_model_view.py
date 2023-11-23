from http import HTTPStatus
from typing import Any, Callable, List, Optional, Type

from django.db.models import Model
from django.http import HttpRequest
from ninja import Router

from ninja_crud.views.abstract_model_view import AbstractModelView
from ninja_crud.views.enums import HTTPMethod
from ninja_crud.views.helpers import utils
from ninja_crud.views.helpers.types import PostDeleteHook, PreDeleteHook


class DeleteModelView(AbstractModelView):
    """
    A view class that handles deleting a specific instance of a model.
    It allows customization through pre- and post-delete hooks and also supports decorators.

    Example:
    ```python
    from ninja_crud import views, viewsets

    from examples.models import Department

    class DepartmentViewSet(viewsets.ModelViewSet):
        model = Department

        # Usage: Delete a department by id
        # DELETE /departments/{id}/
        delete_department_view = views.DeleteModelView()
    ```
    """

    def __init__(
        self,
        pre_delete: Optional[PreDeleteHook] = None,
        post_delete: Optional[PostDeleteHook] = None,
        path: Optional[str] = None,
        decorators: Optional[List[Callable]] = None,
        router_kwargs: Optional[dict] = None,
    ) -> None:
        """
        Initializes the DeleteModelView.

        Args:
            pre_delete (Optional[PreDeleteHook], optional): A function that is called before deleting the instance.
                Defaults to None.

                Should have the signature (request: HttpRequest, instance: Model) -> None.

                If not provided, the function will be a no-op.
            post_delete (Optional[PostDeleteHook], optional): A function that is called after deleting the instance.
                Defaults to None.

                Should have the signature (request: HttpRequest, id: Any, deleted_instance: Model) -> None.

                If not provided, the function will be a no-op.
            path (Optional[str], optional): The path to use for the view. Defaults to "/{id}".
            decorators (Optional[List[Callable]], optional): A list of decorators to apply to the view. Defaults to [].
            router_kwargs (Optional[dict], optional): Additional arguments to pass to the router. Defaults to {}.
        """
        if path is None:
            path = self._get_default_path()
        super().__init__(
            method=HTTPMethod.DELETE,
            path=path,
            detail=True,
            decorators=decorators,
            router_kwargs=router_kwargs,
        )
        self.pre_delete = pre_delete
        self.post_delete = post_delete

    def register_route(self, router: Router, model_class: Type[Model]) -> None:
        @self.configure_route(router=router, model_class=model_class)
        def delete_model(request: HttpRequest, id: utils.get_id_type(model_class)):
            return HTTPStatus.NO_CONTENT, self.delete_model(
                request=request, id=id, model_class=model_class
            )

    def delete_model(
        self, request: HttpRequest, id: Any, model_class: Type[Model]
    ) -> None:
        instance = model_class.objects.get(pk=id)

        if self.pre_delete is not None:
            self.pre_delete(request, instance)

        instance.delete()

        if self.post_delete is not None:
            self.post_delete(request, id, instance)

        return None

    @staticmethod
    def _get_default_path() -> str:
        return "/{id}"

    def get_response(self) -> dict:
        return {HTTPStatus.NO_CONTENT: None}

    def get_operation_id(self, model_class: Type[Model]) -> str:
        return f"delete_{utils.to_snake_case(model_class.__name__)}"

    def get_summary(self, model_class: Type[Model]) -> str:
        return f"Delete {model_class.__name__}"
