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

    Args:
        method (HTTPMethod): View HTTP method. Defaults to HTTPMethod.PUT.
        path (str, optional): View path. Defaults to "/{id}".
        path_parameters (Optional[Type[ninja.Schema]], optional): Schema for
            deserializing path parameters. Automatically inferred from the path
            and the fields of the `ModelViewSet`'s associated model if not provided.
            Defaults to None.
        request_body (Optional[Type[ninja.Schema]], optional): Schema for
            deserializing the request body. Inherits `ModelViewSet`'s default if
            unspecified. Defaults to None.
        response_body (Optional[Type[ninja.Schema]], optional): Schema for serializing
            the response body. Inherits `ModelViewSet`'s default if unspecified.
            Defaults to None.
        get_model (Optional[Callable[[Optional[ninja.Schema]],
            django.db.models.Model]], optional):
            Function to retrieve the model instance. Defaults to `default_get_model`.
            Should have the signature (path_parameters: Optional[Schema]) -> Model.
        pre_save (Optional[Callable[[django.http.HttpRequest, Optional[ninja.Schema],
            django.db.models.Model], None]], optional):
            Hook executed before saving the updated instance. Should have the signature
            (request: HttpRequest, path_parameters: Optional[Schema], instance: Model) -> None.
        post_save (Optional[Callable[[django.http.HttpRequest, Optional[ninja.Schema],
            django.db.models.Model], None]], optional):
            Hook executed after saving the updated instance. Should have the signature
            (request: HttpRequest, path_parameters: Optional[Schema], instance: Model) -> None.
        decorators (Optional[List[Callable]], optional): Decorators for the view.
            Defaults to [].
        router_kwargs (Optional[Dict], optional): Additional router arguments, with
            overrides for 'path', 'methods', and 'response' being ignored. Defaults
            to {}.

    Raises:
        django.db.models.ObjectDoesNotExist: If the instance is not found.
        django.db.models.MultipleObjectsReturned: If multiple instances are found.
        django.core.exceptions.ValidationError: For model validation issues on clean.
        django.db.utils.IntegrityError: For database integrity violations on save.
        ninja.errors.ValidationError: For request components validation issues.

    Important:
        This view does not automatically handle exceptions. It's recommended to
        implement appropriate
        [Exception Handlers](https://django-ninja.dev/guides/errors/) in your project to
        manage such cases effectively, according to your application's needs and
        conventions. See the [Setup](https://django-ninja-crud.readme.io/docs/03-setup)
        guide for more information.

    Example Usage:
    ```python
    # Basic usage using request and response schemas
    update_department = UpdateModelView(
        request_body=DepartmentRequestBody,
        response_body=DepartmentResponseBody,
    )

    # Advanced usage with custom get_model, pre_save, and post_save logic
    update_department = UpdateModelView(
        request_body=DepartmentRequestBody,
        response_body=DepartmentResponseBody,
        get_model=lambda path_parameters: Department.objects.get(id=path_parameters.id),
        pre_save=lambda request, path_parameters, instance: None,
        post_save=lambda request, path_parameters, instance: None,
    )
    ```

    Note:
        The attribute name (e.g., `update_department`) determines the route's name
        and operation ID in the OpenAPI schema, allowing easy API documentation.
    """

    def __init__(
        self,
        method: HTTPMethod = HTTPMethod.PUT,
        path: str = "/{id}",
        path_parameters: Optional[Schema] = None,
        request_body: Optional[Type[Schema]] = None,
        response_body: Optional[Type[Schema]] = None,
        get_model: Optional[Callable[[Optional[Schema]], Model]] = None,
        pre_save: Optional[
            Callable[[HttpRequest, Optional[Schema], Model], None]
        ] = None,
        post_save: Optional[
            Callable[[HttpRequest, Optional[Schema], Model], None]
        ] = None,
        decorators: Optional[List[Callable]] = None,
        router_kwargs: Optional[Dict] = None,
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
        self.get_model = get_model or self.default_get_model
        self.pre_save = pre_save or self.default_pre_save
        self.post_save = post_save or self.default_post_save

    def default_get_model(
        self,
        path_parameters: Optional[Schema],
    ) -> Model:
        """
        Default function to retrieve the model instance to be updated.

        This method can be overridden with custom logic to retrieve the model instance,
        allowing for advanced retrieval logic, such as adding annotations, filtering
        based on request specifics, or implementing permissions checks, to suit specific
        requirements and potentially improve efficiency and security.

        Args:
            path_parameters (Optional[ninja.Schema]): Deserialized path parameters.

        Returns:
            django.db.models.Model: The model instance to be updated.

        Raises:
            django.db.models.ObjectDoesNotExist: If no model instance is found.
            django.db.models.MultipleObjectsReturned: If multiple model instances
                are found.
        """
        return self.model_viewset_class.model.objects.get(
            **(path_parameters.dict() if path_parameters else {})
        )

    @staticmethod
    def default_pre_save(
        request: HttpRequest,
        path_parameters: Optional[Schema],
        instance: Model,
    ) -> None:
        """
        Default pre-save hook that is called before the model instance is saved.
        Full model validation is performed by default with `instance.full_clean()`.

        This method can be overridden with custom pre-save logic, such as implementing
        additional checks, permissions, or side effects.

        Args:
            request (django.http.HttpRequest): The request object.
            path_parameters (Optional[ninja.Schema]): Deserialized path parameters.
            instance (django.db.models.Model): The model instance to be updated, with
                the changes already applied but not yet saved.

        Returns:
            None
        """
        instance.full_clean()

    @staticmethod
    def default_post_save(
        request: HttpRequest,
        path_parameters: Optional[Schema],
        instance: Model,
    ) -> None:
        """
        Default post-save hook that is called after the model instance is saved.
        No-op by default.

        This method can be overridden with custom post-save logic, such as
        implementing additional side effects, logging, or sending notifications.

        Args:
            request (django.http.HttpRequest): The request object.
            path_parameters (Optional[ninja.Schema]): Deserialized path parameters.
            instance (django.db.models.Model): The updated model instance, with
                the changes already applied and saved.

        Returns:
            None
        """
        pass

    def handle_request(
        self,
        request: HttpRequest,
        path_parameters: Optional[Schema],
        query_parameters: Optional[Schema],
        request_body: Optional[Schema],
    ) -> Model:
        instance = self.get_model(path_parameters)

        if request_body:
            for field, value in request_body.dict(exclude_unset=True).items():
                setattr(instance, field, value)

        self.pre_save(request, path_parameters, instance)

        instance.save()

        self.post_save(request, path_parameters, instance)

        return instance

    def _inherit_model_viewset_class_attributes(self) -> None:
        if self.request_body is None:
            self.request_body = self.model_viewset_class.default_request_body
        if self.response_body is None:
            self.response_body = self.model_viewset_class.default_response_body
