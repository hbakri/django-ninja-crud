import http
from typing import Callable, Dict, List, Optional, Type

from django.db.models import Model
from django.http import HttpRequest
from ninja import Schema

from ninja_crud.views.abstract_model_view import AbstractModelView
from ninja_crud.views.enums import HTTPMethod


class RetrieveModelView(AbstractModelView):
    """
    A view class that handles retrieving a model instance.

    Designed to be used as an attribute of a
    [`ninja_crud.viewsets.ModelViewSet`](https://django-ninja-crud.readme.io/reference/model-viewset),
    this class should not be used directly as a standalone view. It is crafted for
    flexibility and allows extensive customization through overrideable methods for
    actions including but not limited to permission checks, advanced model instance
    retrieval. Subclassing is recommended to encapsulate repetitive customizations.

    Args:
        path (str, optional): View path. Defaults to `"/{id}"`.
        path_parameters (Optional[Type[ninja.Schema]], optional): Schema for
            deserializing path parameters. By default, it is automatically inferred from
            the path and the fields of the ModelViewSet's associated model. Defaults to
            `None`.
        query_parameters (Optional[Type[ninja.Schema]], optional): Schema for
            deserializing query parameters. Defaults to `None`.
        response_body (Optional[Type[ninja.Schema]], optional): Schema for serializing
            the response body. By default, it inherits the ModelViewSet's default
            response body. Defaults to `None`.
        decorators (Optional[List[Callable]], optional): Decorators for the view.
            Defaults to `[]`.
        router_kwargs (Optional[Dict], optional): Additional router arguments, with
            overrides for 'path', 'methods', and 'response' being ignored. Defaults
            to `{}`.
        retrieve_model (Optional[Callable], optional): Function to retrieve the model
            instance based on the request, path parameters, and query parameters. This
            method can be overridden with custom logic, allowing for advanced retrieval
            logic, such as adding annotations, filtering based on request specifics, or
            implementing permissions checks, to suit specific requirements and
            potentially improve efficiency and security. By default, it retrieves the
            model instance using the ModelViewSet's model and the path parameters.
            Should have the signature:
            - `(request: HttpRequest, path_parameters: Optional[Schema],
                query_parameters: Optional[Schema]) -> Model`.

    Raises:
        django.db.models.ObjectDoesNotExist: If the instance is not found.
        django.db.models.MultipleObjectsReturned: If multiple instances are found.
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
        retrieve_department = views.RetrieveModelView(
            response_body=DepartmentOut,
        )

        # Basic usage with explicit default settings
        retrieve_department = views.RetrieveModelView(
            path="/{id}",
            response_body=DepartmentOut,
            retrieve_model=lambda request, path_parameters, query_parameters: Department.objects.get(
                id=path_parameters.id
            ),
        )

        # Usage with default response body schema set in the ModelViewSet
        default_response_body = DepartmentOut
        retrieve_department = views.RetrieveModelView()

        # Custom queryset retrieval for annotated fields or any advanced logic
        retrieve_department = views.RetrieveModelView(
            response_body=DepartmentOut,
            retrieve_model=lambda request, path_parameters, query_parameters: Department.objects.annotate(
                count_employees=Count("employees")
            ).get(id=path_parameters.id),
        )

        # Authentication at the view level
        retrieve_department = views.RetrieveModelView(
            response_body=DepartmentOut,
            router_kwargs={"auth": ninja.security.django_auth},
        )

        # Advanced usage with external service
        retrieve_department = views.RetrieveModelView(
            response_body=DepartmentOut,
            retrieve_model=lambda request, path_parameters, query_parameters: external_service.retrieve_department(
                ...
            ),
        )
    ```

    Note:
        The name of the class attribute (e.g., `retrieve_department`) determines the
        route's name and operation ID in the OpenAPI schema. Can be any valid Python
        attribute name, but it is recommended to use a name that reflects the action
        being performed.
    """

    def __init__(
        self,
        path: str = "/{id}",
        path_parameters: Optional[Type[Schema]] = None,
        query_parameters: Optional[Type[Schema]] = None,
        response_body: Optional[Type[Schema]] = None,
        decorators: Optional[List[Callable]] = None,
        router_kwargs: Optional[Dict] = None,
        retrieve_model: Optional[
            Callable[[HttpRequest, Optional[Schema], Optional[Schema]], Model]
        ] = None,
    ) -> None:
        super().__init__(
            method=HTTPMethod.GET,
            path=path,
            path_parameters=path_parameters,
            query_parameters=query_parameters,
            request_body=None,
            response_body=response_body,
            response_status=http.HTTPStatus.OK,
            decorators=decorators,
            router_kwargs=router_kwargs,
        )
        self.retrieve_model = retrieve_model or self._default_retrieve_model

    def _default_retrieve_model(
        self,
        request: HttpRequest,
        path_parameters: Optional[Schema],
        query_parameters: Optional[Schema],
    ) -> Model:
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
        return self.retrieve_model(request, path_parameters, query_parameters)

    def _inherit_model_viewset_class_attributes(self) -> None:
        if self.response_body is None:
            self.response_body = self.model_viewset_class.default_response_body
