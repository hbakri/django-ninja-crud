from http import HTTPStatus
from typing import Any, Callable, List, Optional, Type, TypeVar

from django.db.models import Model
from django.http import HttpRequest
from ninja import Router

from ninja_crud.views import utils
from ninja_crud.views.abstract import AbstractModelView

ModelType = TypeVar("ModelType", bound=Model)
PreDeleteHook = Callable[[HttpRequest, ModelType], None]
PostDeleteHook = Callable[[HttpRequest, Any], None]


class DeleteModelView(AbstractModelView):
    """
    A view class that handles deleting a specific instance of a model.

    Attributes:
        decorators (List[Callable], optional): A list of decorators to apply to the view function.
        pre_delete (PreDeleteHook, optional): A function to call before deleting the instance. Should have the signature (request: HttpRequest, instance: ModelType).
        post_delete (PostDeleteHook, optional): A function to call after deleting the instance. Should have the signature (request: HttpRequest, id: Any).
        router_kwargs (Optional[dict], optional): A dictionary of keyword arguments to pass to the router.
    """

    def __init__(
        self,
        decorators: List[Callable] = None,
        pre_delete: PreDeleteHook = None,
        post_delete: PostDeleteHook = None,
        router_kwargs: Optional[dict] = None,
    ) -> None:
        """
        Initializes the DeleteModelView with the given decorators and optional pre- and post-delete hooks.

        Args:
            decorators (List[Callable], optional): A list of decorators to apply to the view function.
            pre_delete (PreDeleteHook, optional): A function to call before deleting the instance. Should have the signature (request: HttpRequest, instance: ModelType).
            post_delete (PostDeleteHook, optional): A function to call after deleting the instance. Should have the signature (request: HttpRequest, id: Any).
            router_kwargs (Optional[dict], optional): A dictionary of keyword arguments to pass to the router.
        """
        super().__init__(decorators=decorators, router_kwargs=router_kwargs)
        self.pre_delete = pre_delete
        self.post_delete = post_delete

    def register_route(self, router: Router, model_class: Type[Model]) -> None:
        """
        Registers the delete route for the given model class.

        Args:
            router (Router): The Ninja router to register the route with.
            model_class (Type[Model]): The Django model class for the update view.

        Note:
            This method is usually called by the parent class and should not be called manually.
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
        """
        Returns the URL path for this view, used in routing.

        Returns:
            str: The URL path.
        """
        return "/{id}"
