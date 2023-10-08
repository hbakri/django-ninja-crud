from http import HTTPStatus
from typing import Callable, List, Optional, Type

from django.db.models import Model
from django.http import HttpRequest
from ninja import Router

from ninja_crud.views import utils
from ninja_crud.views.abstract import AbstractModelView
from ninja_crud.views.enums import HTTPMethod
from ninja_crud.views.types import PostDeleteHook, PreDeleteHook


class DeleteModelView(AbstractModelView):
    """
    A view class that handles deleting a specific instance of a model.
    It allows customization through pre- and post-delete hooks and also supports decorators.

    Example:
    ```python
    from ninja_crud.views import ModelViewSet, DeleteModelView
    from example.models import Department, Employee
    from example.schemas import DepartmentOut, EmployeeOut

    class DepartmentViewSet(ModelViewSet):
        model_class = Department

        # Usage: Delete a department by id
        # DELETE /departments/{id}/
        delete = DeleteModelView(output_schema=DepartmentOut)
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
            pre_delete (PreDeleteHook, optional): A function that is called before deleting the instance.
                Defaults to None.

                Should have the signature (request: HttpRequest, instance: Model) -> None.

                If not provided, the function will be a no-op.
            post_delete (PostDeleteHook, optional): A function that is called after deleting the instance.
                Defaults to None.

                Should have the signature (request: HttpRequest, id: Any, deleted_instance: Model) -> None.

                If not provided, the function will be a no-op.
            path (str, optional): The path to use for the view. Defaults to "/{id}".
            decorators (List[Callable], optional): A list of decorators to apply to the view. Defaults to [].
            router_kwargs (dict, optional): Additional arguments to pass to the router. Defaults to {}.
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
        @router.api_operation(
            **self._sanitize_and_merge_router_kwargs(
                default_router_kwargs=self._get_default_router_kwargs(model_class),
                custom_router_kwargs=self.router_kwargs,
            )
        )
        @utils.merge_decorators(self.decorators)
        def delete_model(request: HttpRequest, id: utils.get_id_type(model_class)):
            instance = model_class.objects.get(pk=id)

            if self.pre_delete is not None:
                self.pre_delete(request, instance)

            instance.delete()

            if self.post_delete is not None:
                self.post_delete(request, id, instance)

            return HTTPStatus.NO_CONTENT, None

    @staticmethod
    def _get_default_path() -> str:
        return "/{id}"

    def _get_default_router_kwargs(self, model_class: Type[Model]) -> dict:
        return dict(
            methods=[self.method.value],
            path=self.path,
            response={HTTPStatus.NO_CONTENT: None},
            operation_id=self._get_operation_id(model_class),
            summary=self._get_summary(model_class),
        )

    @staticmethod
    def _get_operation_id(model_class: Type[Model]) -> str:
        return f"delete_{utils.to_snake_case(model_class.__name__)}"

    @staticmethod
    def _get_summary(model_class: Type[Model]) -> str:
        return f"Delete {model_class.__name__}"
