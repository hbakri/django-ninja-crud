import http
from typing import Callable, Dict, List, Optional, Type

from django.db.models import Model
from django.http import HttpRequest
from ninja import Schema

from ninja_crud.views.abstract_model_view import AbstractModelView
from ninja_crud.views.enums import HTTPMethod


class UpdateModelView(AbstractModelView):
    """
    A view class that handles updating a model instance.

    Designed to be used as an attribute of a
    [`ninja_crud.viewsets.ModelViewSet`](https://django-ninja-crud.readme.io/reference/model-viewset),
    this class should not be used directly as a standalone view. It is crafted for
    flexibility and allows extensive customization through overrideable methods for
    actions including but not limited to permission checks, advanced model instance
    retrieval and updating, and hooks for custom logic, both before and after saving.
    Subclassing is recommended to encapsulate repetitive customizations.

    Args:
        method (HTTPMethod, optional): View HTTP method. Defaults to HTTPMethod.PUT.
        path (str, optional): View path. Defaults to `"/{id}"`.
        path_parameters (Optional[Type[ninja.Schema]], optional): Schema for
            deserializing path parameters. By default, it is automatically inferred from
            the path and the fields of the ModelViewSet's associated model. Defaults to
            `None`.
        request_body (Optional[Type[ninja.Schema]], optional): Schema for
            deserializing the request body. By default, it inherits the ModelViewSet's
            default request body. Defaults to `None`.
        response_body (Optional[Type[ninja.Schema]], optional): Schema for serializing
            the response body. By default, it inherits the ModelViewSet's default
            response body. Defaults to `None`.
        decorators (Optional[List[Callable]], optional): Decorators for the view.
            Defaults to `[]`.
        router_kwargs (Optional[Dict], optional): Additional router arguments, with
            overrides for 'path', 'methods', and 'response' being ignored. Defaults
            to `{}`.
        get_model (Optional[Callable], optional): Function to retrieve the model
            instance based on the request and path parameters. This method can be
            overridden with custom logic, allowing for advanced retrieval logic, such as
            adding annotations, filtering based on request specifics, or implementing
            permissions checks, to suit specific requirements. By default, it retrieves
            the model instance using the ModelViewSet's model and the path parameters.
            Should have the signature:
            - `(request: HttpRequest, path_parameters: Optional[Schema]) -> Model`.
        pre_save (Optional[Callable], optional): Hook executed before saving the updated
            instance, allowing for custom logic such as permission checks, logging, or
            side effects. By default, it performs full model validation with
            [`.full_clean()`](https://docs.djangoproject.com/en/5.0/ref/models/instances/#django.db.models.Model.full_clean).
            Should have the signature:
            - `(request: HttpRequest, instance: Model) -> None`.
        post_save (Optional[Callable], optional): Hook executed after saving the updated
            instance, allowing for custom logic such as sending notifications, logging,
            or side effects. No-op by default. Should have the signature:
            - `(request: HttpRequest, instance: Model) -> None`.
        update_model (Optional[Callable], optional): Function to update the model
            instance. This method can be overridden with custom logic, allowing for
            advanced and complex updates, such as partial updates, custom validation, or
            additional checks, to suit specific requirements. By default, it retrieves
            the model instance using `get_model`, updates the instance using the request
            body, calls `pre_save`, saves the instance using
            [`.save()`](https://docs.djangoproject.com/en/5.0/ref/models/instances/#django.db.models.Model.save)
            and then calls `post_save`. When overriding this method, note that the
            get_model, pre- and post-hooks are not called anymore.
            Should have the signature:
            - `(request: HttpRequest, path_parameters: Optional[Schema],
                request_body: Optional[Schema]) -> Model`.

    Raises:
        django.db.models.ObjectDoesNotExist: If the instance is not found.
        django.db.models.MultipleObjectsReturned: If multiple instances are found.
        django.core.exceptions.ValidationError: For model validation issues on clean.
        django.db.utils.IntegrityError: For database integrity violations on save.
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
        update_department = views.UpdateModelView(
            request_body=DepartmentIn,
            response_body=DepartmentOut,
        )

        # Basic usage with explicit default settings
        update_department = views.UpdateModelView(
            path="/{id}",
            request_body=DepartmentIn,
            response_body=DepartmentOut,
            get_model=lambda request, path_parameters: Department.objects.get(
                id=path_parameters.id
            ),
            pre_save=lambda request, instance: instance.full_clean(),
            post_save=lambda request, instance: None,
        )

        # Usage with default request and response body schemas set in the ModelViewSet
        default_request_body = DepartmentIn
        default_response_body = DepartmentOut
        update_department = views.UpdateModelView()

        # Authentication at the view level
        update_department = views.UpdateModelView(
            request_body=DepartmentIn,
            response_body=DepartmentOut,
            router_kwargs={"auth": ninja.security.django_auth},
        )

        # Advanced usage with external service
        update_department = views.UpdateModelView(
            request_body=DepartmentIn,
            response_body=DepartmentOut,
            update_model=lambda request, path_parameters, request_body: external_service.update_department(
                ...
            ),
        )
    ```

    Note:
        The name of the class attribute (e.g., `update_department`) determines the
        route's name and operation ID in the OpenAPI schema. Can be any valid Python
        attribute name, but it is recommended to use a name that reflects the action
        being performed.
    """

    def __init__(
        self,
        method: HTTPMethod = HTTPMethod.PUT,
        path: str = "/{id}",
        path_parameters: Optional[Schema] = None,
        request_body: Optional[Type[Schema]] = None,
        response_body: Optional[Type[Schema]] = None,
        decorators: Optional[List[Callable]] = None,
        router_kwargs: Optional[Dict] = None,
        get_model: Optional[Callable[[HttpRequest, Optional[Schema]], Model]] = None,
        pre_save: Optional[Callable[[HttpRequest, Model], None]] = None,
        post_save: Optional[Callable[[HttpRequest, Model], None]] = None,
        update_model: Optional[
            Callable[[HttpRequest, Optional[Schema], Optional[Schema]], Model]
        ] = None,
    ) -> None:
        super().__init__(
            method=method,
            path=path,
            path_parameters=path_parameters,
            query_parameters=None,
            request_body=request_body,
            response_body=response_body,
            response_status=http.HTTPStatus.OK,
            decorators=decorators,
            router_kwargs=router_kwargs,
        )
        self.get_model = get_model or self._default_get_model
        self.pre_save = pre_save or self._default_pre_save
        self.post_save = post_save or self._default_post_save
        self.update_model = update_model or self._default_update_model

    def _default_get_model(
        self, request: HttpRequest, path_parameters: Optional[Schema]
    ) -> Model:
        return self.model_viewset_class.model.objects.get(
            **(path_parameters.dict() if path_parameters else {})
        )

    @staticmethod
    def _default_pre_save(request: HttpRequest, instance: Model) -> None:
        instance.full_clean()

    @staticmethod
    def _default_post_save(request: HttpRequest, instance: Model) -> None:
        pass

    def _default_update_model(
        self,
        request: HttpRequest,
        path_parameters: Optional[Schema],
        request_body: Optional[Schema],
    ) -> Model:
        instance = self.get_model(request, path_parameters)

        if request_body:
            for field, value in request_body.dict(exclude_unset=True).items():
                setattr(instance, field, value)

        self.pre_save(request, instance)
        instance.save()
        self.post_save(request, instance)
        return instance

    def handle_request(
        self,
        request: HttpRequest,
        path_parameters: Optional[Schema],
        query_parameters: Optional[Schema],
        request_body: Optional[Schema],
    ) -> Model:
        return self.update_model(request, path_parameters, request_body)

    def _inherit_model_viewset_class_attributes(self) -> None:
        if self.request_body is None:
            self.request_body = self.model_viewset_class.default_request_body
        if self.response_body is None:
            self.response_body = self.model_viewset_class.default_response_body
