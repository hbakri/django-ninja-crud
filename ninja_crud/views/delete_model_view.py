from http import HTTPStatus
from typing import Any, Callable, List, Optional, Type

from django.db.models import Model
from django.http import HttpRequest

from ninja_crud.views.abstract_model_view import AbstractModelView
from ninja_crud.views.enums import HTTPMethod
from ninja_crud.views.helpers import utils
from ninja_crud.views.helpers.types import PostDeleteHook, PreDeleteHook
from ninja_crud.views.validators.path_validator import PathValidator


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
        # DELETE /{id}/
        delete_department = views.DeleteModelView()
    ```

    Note:
        The attribute name (e.g., `delete_department`) is flexible and customizable.
        It serves as the name of the route and the operation id in the OpenAPI schema.
    """

    def __init__(
        self,
        pre_delete: Optional[PreDeleteHook] = None,
        post_delete: Optional[PostDeleteHook] = None,
        path: str = "/{id}",
        decorators: Optional[List[Callable]] = None,
        router_kwargs: Optional[dict] = None,
    ) -> None:
        """
        Initializes the DeleteModelView.

        Args:
            pre_delete (Optional[PreDeleteHook], optional): A function that is called before deleting the instance.
                Defaults to None.

                The function should have the signature:
                - (request: HttpRequest, instance: Model) -> None.

                If not provided, the function will be a no-op.
            post_delete (Optional[PostDeleteHook], optional): A function that is called after deleting the instance.
                Defaults to None.

                The function should have the signature:
                - (request: HttpRequest, id: Any, deleted_instance: Model) -> None.

                If not provided, the function will be a no-op.
            path (str, optional): The path to use for the view. Defaults to "/{id}". Must include a "{id}" parameter.
            decorators (Optional[List[Callable]], optional): A list of decorators to apply to the view. Defaults to [].
            router_kwargs (Optional[dict], optional): Additional arguments to pass to the router. Defaults to {}.
                Overrides are allowed for most arguments except 'path', 'methods', and 'response'. If any of these
                arguments are provided, a warning will be logged and the override will be ignored.
        """
        super().__init__(
            method=HTTPMethod.DELETE,
            path=path,
            filter_schema=None,
            payload_schema=None,
            response_schema=None,
            decorators=decorators,
            router_kwargs=router_kwargs,
        )

        PathValidator.validate(path=path, allow_no_parameters=False)

        self.pre_delete = pre_delete
        self.post_delete = post_delete

    def build_view(self, model_class: Type[Model]) -> Callable:
        def view(request: HttpRequest, id: utils.get_id_type(model_class)):
            return HTTPStatus.NO_CONTENT, self.delete_model(
                request=request, id=id, model_class=model_class
            )

        return view

    def delete_model(
        self, request: HttpRequest, id: Any, model_class: Type[Model]
    ) -> None:
        instance = model_class.objects.get(pk=id)

        if self.pre_delete is not None:
            self.pre_delete(request, instance)

        instance.delete()

        if self.post_delete is not None:
            self.post_delete(request, id, instance)

    def get_response(self) -> dict:
        """
        Provides a mapping of HTTP status codes to response schemas for the delete view.

        This response schema is used in API documentation to describe the response body for this view.
        The response schema is critical and cannot be overridden using `router_kwargs`. Any overrides
        will be ignored.

        Returns:
            dict: A mapping of HTTP status codes to response schemas for the delete view.
                Defaults to {204: None}.
        """
        return {HTTPStatus.NO_CONTENT: None}
