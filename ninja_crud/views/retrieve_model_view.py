from http import HTTPStatus
from typing import Callable, Dict, List, Optional, Type

from django.db.models import Model
from django.http import HttpRequest
from ninja import Schema

from ninja_crud.views.abstract_model_view import AbstractModelView
from ninja_crud.views.enums import HTTPMethod


class RetrieveModelView(AbstractModelView):
    """
    A view class that handles retrieving a model instance.

    Args:
        path (str, optional): View path. Defaults to "/{id}".
        path_parameters (Optional[Type[ninja.Schema]], optional): Schema for
            deserializing path parameters. Automatically inferred from the path
            and the fields of the `ModelViewSet`'s associated model if not provided.
            Defaults to None.
        response_body (Optional[Type[ninja.Schema]], optional): Schema for serializing
            the response body. Inherits `ModelViewSet`'s default if unspecified.
            Defaults to None.
        get_model (Optional[Callable[[Optional[ninja.Schema]], django.db.models.Model]],
            optional):
            Function to retrieve the model instance. Defaults to `default_get_model`.
            Should have the signature (path_parameters: Optional[Schema]) -> Model.
        decorators (Optional[List[Callable]], optional): Decorators for the view.
            Defaults to [].
        router_kwargs (Optional[Dict], optional): Additional router arguments, with
            overrides for 'path', 'methods', and 'response' being ignored. Defaults
            to {}.

    Raises:
        django.db.models.ObjectDoesNotExist: If the instance is not found.
        django.db.models.MultipleObjectsReturned: If multiple instances are found.
        ninja.errors.ValidationError: For request components validation issues.

    Important:
        Exceptions above are not handled by this view. Please define exception handlers
        in your Django Ninja app for appropriate error management, ensuring responses
        fit your app's needs and conventions.

    Example Usage:
    ```python
    retrieve_department = views.RetrieveModelView(
        response_body=DepartmentResponseBody,
    )

    # or with custom get_model logic
    retrieve_department = views.RetrieveModelView(
        response_body=DepartmentResponseBody,
        get_model=lambda path_parameters: Department.objects.get(id=path_parameters.id),
    )
    ```

    Note:
        The attribute name (e.g., `retrieve_department`) determines the route's name
        and operation ID in the OpenAPI schema, allowing easy API documentation.
    """

    def __init__(
        self,
        path: str = "/{id}",
        path_parameters: Optional[Type[Schema]] = None,
        response_body: Optional[Type[Schema]] = None,
        get_model: Optional[Callable[[Optional[Schema]], Model]] = None,
        decorators: Optional[List[Callable]] = None,
        router_kwargs: Optional[Dict] = None,
    ) -> None:
        super().__init__(
            method=HTTPMethod.GET,
            path=path,
            path_parameters=path_parameters,
            query_parameters=None,
            request_body=None,
            response_body=response_body,
            response_status=HTTPStatus.OK,
            decorators=decorators,
            router_kwargs=router_kwargs,
        )
        self.get_model = get_model or self.default_get_model

    def default_get_model(self, path_parameters: Optional[Schema]) -> Model:
        """
        Default function to retrieve the model instance.

        This method can be overridden with custom logic to retrieve the model instance,
        allowing for advanced retrieval logic, such as adding annotations, filtering
        based on request specifics, or implementing permissions checks, to suit specific
        requirements and potentially improve efficiency and security.

        Args:
            path_parameters (Optional[ninja.Schema]): Deserialized path parameters.

        Returns:
            django.db.models.Model: The model instance to be retrieved.

        Raises:
            django.db.models.ObjectDoesNotExist: If no model instance is found.
            django.db.models.MultipleObjectsReturned: If multiple model instances
                are found.
        """
        return self.model_viewset_class.model.objects.get(
            **(path_parameters.dict() if path_parameters else {})
        )

    def handle_request(
        self,
        request: HttpRequest,
        path_parameters: Optional[Schema],
        query_parameters: Optional[Schema],
        request_body: Optional[Schema],
    ) -> Model:
        return self.get_model(path_parameters)

    def _inherit_model_viewset_class_attributes(self) -> None:
        if self.response_body is None:
            self.response_body = self.model_viewset_class.default_response_body
