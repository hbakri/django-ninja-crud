import http
from typing import Callable, Dict, List, Optional

from django.db.models import Model
from django.http import HttpRequest
from ninja import Schema

from ninja_crud.views.abstract_model_view import AbstractModelView
from ninja_crud.views.enums import HTTPMethod


class DeleteModelView(AbstractModelView):
    """
    A view class that handles deleting a model instance.

    Designed to be used as an attribute of a
    [`ninja_crud.viewsets.ModelViewSet`](https://django-ninja-crud.readme.io/reference/model-viewset),
    this class should not be used directly as a standalone view. It is crafted for
    flexibility and allows extensive customization through overrideable methods for
    actions including but not limited to permission checks, advanced model instance
    retrieval and deletion, and hooks for custom logic, both before and after deletion.
    Subclassing is recommended to encapsulate repetitive customizations.

    Args:
        path (str, optional): View path. Defaults to `"/{id}"`.
        path_parameters (Optional[Type[ninja.Schema]], optional): Schema for
            deserializing path parameters. By default, it is automatically inferred from
            the path and the fields of the ModelViewSet's associated model. Defaults to
            `None`.
        decorators (Optional[List[Callable]], optional): Decorators for the view.
            Defaults to `[]`.
        router_kwargs (Optional[Dict], optional): Additional router arguments, with
            overrides for 'path', 'methods', and 'response' being ignored. Defaults
            to `{}`.
        get_model (Optional[Callable], optional): Function to retrieve the model
            instance based on the request and path parameters. This method can be
            overridden with custom logic to retrieve the model instance, allowing for
            advanced retrieval logic, such as adding annotations, filtering based on
            request specifics, or implementing permissions checks, to suit specific
            requirements and potentially improve efficiency and security. By default,
            it retrieves the model instance using the ModelViewSet's model and the path
            parameters. Should have the signature:
            - `(request: HttpRequest, path_parameters: Optional[Schema]) -> Model`.
        pre_delete (Optional[Callable], optional): Hook executed before deleting the
            instance, allowing for custom logic such as permission checks, logging, or
            side effects. No-op by default. Should have the signature:
            - `(request: HttpRequest, instance: Model) -> None`.
        post_delete (Optional[Callable], optional): Hook executed after deleting the
            instance, allowing for custom logic such as sending notifications, logging,
            or side effects. No-op by default. Should have the signature:
            - `(request: HttpRequest, instance: Model) -> None`.
        delete_model (Optional[Callable], optional): Function to delete the model
            instance. This method can be overridden with custom logic, allowing for
            advanced deletion logic, such as implementing soft deletes, cascading
            deletes, or additional checks, to suit specific requirements. By default,
            it retrieves the model instance using `get_model`, calls `pre_delete`,
            deletes the instance using
            [`.delete()`](https://docs.djangoproject.com/en/5.0/ref/models/instances/#django.db.models.Model.delete)
            and then calls `post_delete`. When overriding this method, note that the
            get_model, pre- and post-hooks are not called anymore.
            Should have the signature:
            - `(request: HttpRequest, path_parameters: Optional[Schema]) -> None`.

    Raises:
        django.db.models.ObjectDoesNotExist: If the instance is not found.
        django.db.models.MultipleObjectsReturned: If multiple instances are found.
        django.db.utils.IntegrityError: For database integrity violations on delete.
        ninja.errors.ValidationError: For request components validation issues.

    Since this view does not automatically handle exceptions, implementation requires
    appropriate [exception handlers](https://django-ninja.dev/guides/errors/) for
    comprehensive error management according to your application's conventions.
    Refer to the [setup guide](https://django-ninja-crud.readme.io/docs/03-setup).

    Example:
    ```python
    class DepartmentViewSet(viewsets.ModelViewSet):
        model = Department

        # Basic usage with implicit default settings
        delete_department = views.DeleteModelView()

        # Basic usage with explicit default settings
        delete_department = views.DeleteModelView(
            path="/{id}",
            get_model=lambda request, path_parameters: Department.objects.get(
                id=path_parameters.id
            ),
            pre_delete=lambda request, instance: None,
            post_delete=lambda request, instance: None,
        )

        # Soft delete example (subclass would be more appropriate)
        @staticmethod
        def soft_delete_model(request, instance):
            instance.is_active = False
            instance.save()

        soft_delete_department = views.DeleteModelView(
            path="/{id}/soft",
            get_model=lambda request, path_parameters: Department.objects.get(
                id=path_parameters.id, is_active=True
            ),
            delete_model=soft_delete_model,
        )

        # Authentication at the view level
        delete_department = views.DeleteModelView(
            router_kwargs={"auth": ninja.security.django_auth},
        )

        # Advanced usage with external service
        delete_department = views.DeleteModelView(
            delete_model=lambda request, path_parameters: external_service.delete_department(
                ...
            ),
        )
    ```

    Note:
        The name of the class attribute (e.g., `delete_department`) determines the
        route's name and operation ID in the OpenAPI schema. Can be any valid Python
        attribute name, but it is recommended to use a name that reflects the action
        being performed.
    """

    def __init__(
        self,
        path: str = "/{id}",
        path_parameters: Optional[Schema] = None,
        decorators: Optional[List[Callable]] = None,
        router_kwargs: Optional[Dict] = None,
        get_model: Optional[Callable[[HttpRequest, Optional[Schema]], Model]] = None,
        pre_delete: Optional[Callable[[HttpRequest, Model], None]] = None,
        post_delete: Optional[Callable[[HttpRequest, Model], None]] = None,
        delete_model: Optional[Callable[[HttpRequest, Optional[Schema]], None]] = None,
    ) -> None:
        super().__init__(
            method=HTTPMethod.DELETE,
            path=path,
            path_parameters=path_parameters,
            query_parameters=None,
            request_body=None,
            response_body=None,
            response_status=http.HTTPStatus.NO_CONTENT,
            decorators=decorators,
            router_kwargs=router_kwargs,
        )
        self.get_model = get_model or self._default_get_model
        self.pre_delete = pre_delete or self._default_pre_delete
        self.post_delete = post_delete or self._default_post_delete
        self.delete_model = delete_model or self._default_delete_model

    def _default_get_model(
        self, request: HttpRequest, path_parameters: Optional[Schema]
    ) -> Model:
        return self.model_viewset_class.model.objects.get(
            **(path_parameters.dict() if path_parameters else {})
        )

    @staticmethod
    def _default_pre_delete(request: HttpRequest, instance: Model) -> None:
        pass

    @staticmethod
    def _default_post_delete(request: HttpRequest, instance: Model) -> None:
        pass

    def _default_delete_model(
        self, request: HttpRequest, path_parameters: Optional[Schema]
    ) -> None:
        instance = self.get_model(request, path_parameters)

        self.pre_delete(request, instance)
        instance.delete()
        self.post_delete(request, instance)

    def handle_request(
        self,
        request: HttpRequest,
        path_parameters: Optional[Schema],
        query_parameters: Optional[Schema],
        request_body: Optional[Schema],
    ) -> None:
        self.delete_model(request, path_parameters)
