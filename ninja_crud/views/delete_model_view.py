from http import HTTPStatus
from typing import Any, Callable, Dict, List, Optional

from django.db.models import Model
from django.http import HttpRequest

from ninja_crud.views.abstract_model_view import AbstractModelView
from ninja_crud.views.enums import HTTPMethod
from ninja_crud.views.validators.path_validator import PathValidator


class DeleteModelView(AbstractModelView):
    """
    A view class that handles deleting a model instance, allowing customization
    through pre- and post-delete hooks and supporting decorators.

    Args:
        path (str, optional): Path for the view. Defaults to "/{id}". Should
            include a "{id}" parameter for a specific model instance.
        pre_delete (Optional[Callable[[HttpRequest, Any, Model], None]], optional):
            Function to execute before deleting the model instance. Defaults to None.
            Should have the signature (request: HttpRequest, id: Any, instance:
            Model) -> None.
        post_delete (Optional[Callable[[HttpRequest, Any, Model], None]], optional):
            Function to execute after deleting the model instance. Defaults to None.
            Should have the signature (request: HttpRequest, id: Any, instance:
            Model) -> None. Be aware that the instance will no longer exist in the
            database and will not have an id.
        decorators (Optional[List[Callable]], optional): Decorators for the view.
            Defaults to [].
        router_kwargs (Optional[Dict], optional): Additional router arguments.
            Defaults to {}. Overrides are ignored for 'path', 'methods', and
            'response'.

    Example:
    ```python
    from typing import Any

    from django.http import HttpRequest
    from ninja_crud import views, viewsets

    from examples.models import Department


    class DepartmentViewSet(viewsets.ModelViewSet):
        model = Department

        # Basic usage: Delete a department
        # Endpoint: DELETE /{id}/
        delete_department = views.DeleteModelView()

        # Advanced usage: With pre- and post-delete hooks
        # Endpoint: DELETE /{id}/
        @staticmethod
        def pre_delete(request: HttpRequest, id: Any, instance: Department):
            pass

        @staticmethod
        def post_delete(request: HttpRequest, id: Any, instance: Department):
            pass

        delete_department = views.DeleteModelView(
            pre_delete=pre_delete,
            post_delete=post_delete,
        )
    ```

    Note:
        The attribute name (e.g. `delete_department`) is flexible and customizable.
        It serves as the name of the route and the operation id in the OpenAPI schema.
    """

    def __init__(
        self,
        path: str = "/{id}",
        pre_delete: Optional[Callable[[HttpRequest, Any, Model], None]] = None,
        post_delete: Optional[Callable[[HttpRequest, Any, Model], None]] = None,
        decorators: Optional[List[Callable]] = None,
        router_kwargs: Optional[Dict] = None,
    ) -> None:
        super().__init__(
            method=HTTPMethod.DELETE,
            path=path,
            query_parameters=None,
            request_body=None,
            response_body=None,
            response_status=HTTPStatus.NO_CONTENT,
            decorators=decorators,
            router_kwargs=router_kwargs,
        )

        PathValidator.validate(path=path, allow_no_parameters=False)

        self.pre_delete = pre_delete
        self.post_delete = post_delete

    def build_view(self) -> Callable:
        id_field_type = self.infer_id_field_type()

        def view(request: HttpRequest, id: id_field_type):
            return self.response_status, self.delete_model(request=request, id=id)

        return view

    def delete_model(self, request: HttpRequest, id: Any) -> None:
        instance = self.model_viewset_class.model.objects.get(pk=id)

        if self.pre_delete is not None:
            self.pre_delete(request, id, instance)

        instance.delete()

        if self.post_delete is not None:
            self.post_delete(request, id, instance)
