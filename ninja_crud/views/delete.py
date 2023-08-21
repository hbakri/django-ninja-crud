from http import HTTPStatus
from typing import Any, Callable, List, Optional, Type, TypeVar

from django.db.models import Model
from django.http import HttpRequest
from ninja import Router

from ninja_crud.views import utils
from ninja_crud.views.abstract import AbstractModelView

# Type alias for a Django Model instance.
# It's a generic type that is bound to Django's base Model class,
# meaning it can represent any Django Model instance.
ModelType = TypeVar("ModelType", bound=Model)

# Type alias for a callable to be invoked before deleting the instance.
# Should have the signature (request: HttpRequest, instance: Model) -> None.
PreDeleteHook = Callable[[HttpRequest, ModelType], None]

# Type alias for a callable to be invoked after deleting the instance.
# Should have the signature (request: HttpRequest, id: Any) -> None.
PostDeleteHook = Callable[[HttpRequest, Any], None]


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
        pre_delete: PreDeleteHook = None,
        post_delete: PostDeleteHook = None,
        decorators: List[Callable] = None,
        router_kwargs: Optional[dict] = None,
    ) -> None:
        """
        Initializes the DeleteModelView with the given decorators and optional pre- and post-delete hooks.

        Args:
            pre_delete (PreDeleteHook, optional): A function that is called before deleting the instance.
                Defaults to None.

                Should have the signature (request: HttpRequest, instance: Model) -> None.

                If not provided, the function will be a no-op.
            post_delete (PostDeleteHook, optional): A function that is called after deleting the instance.
                Defaults to None.

                Should have the signature (request: HttpRequest, id: Any) -> None.

                If not provided, the function will be a no-op.
            decorators (List[Callable], optional): A list of decorators to apply to the view. Defaults to None.
            router_kwargs (Optional[dict], optional): Additional arguments to pass to the router. Defaults to None.
        """
        super().__init__(decorators=decorators, router_kwargs=router_kwargs)
        self.pre_delete = pre_delete
        self.post_delete = post_delete

    def register_route(self, router: Router, model_class: Type[Model]) -> None:
        """
        Registers the delete route for the given model class.

        Args:
            router (Router): The Ninja Router to register the route with.
            model_class (Type[Model]): The Django Model class to use for the route.
        """

        @router.delete(
            path=self.get_path(),
            response={HTTPStatus.NO_CONTENT: None},
            operation_id=f"delete_{utils.to_snake_case(model_class.__name__)}",
            summary=f"Delete {model_class.__name__}",
            **self.router_kwargs,
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
