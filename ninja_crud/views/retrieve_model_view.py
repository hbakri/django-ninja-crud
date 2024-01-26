from http import HTTPStatus
from typing import Any, Callable, Dict, List, Optional, Type

from django.db.models import QuerySet
from django.http import HttpRequest
from ninja import Schema

from ninja_crud.views.abstract_model_view import AbstractModelView
from ninja_crud.views.enums import HTTPMethod
from ninja_crud.views.validators.path_validator import PathValidator
from ninja_crud.views.validators.queryset_getter_validator import (
    QuerySetGetterValidator,
)


class RetrieveModelView(AbstractModelView):
    """
    A view class that handles retrieving a model instance, allowing customization
    through a queryset getter and supporting decorators.

    Args:
        path (str, optional): Path for the view. Defaults to "/{id}". Should
            include a "{id}" parameter for a specific model instance.
        response_body (Optional[Type[ninja.Schema]], optional): Schema for
            serializing the response body. Defaults to None. If not provided,
            inherits from `ModelViewSet`s `default_response_body`.
        queryset_getter (Optional[Callable[[Any], models.QuerySet]], optional):
            Customizes queryset. Defaults to None. Should have the signature
            (id: Any) -> QuerySet. If not provided, the default manager of the
            `ModelViewSet`s `model` will be used.
        decorators (Optional[List[Callable]], optional): Decorators for the view.
            Defaults to [].
        router_kwargs (Optional[Dict], optional): Additional router arguments.
            Defaults to {}. Overrides are ignored for 'path', 'methods', and
            'response'.

    Example:
    ```python
    from django.db.models import Count
    from ninja_crud import views, viewsets

    from examples.models import Department
    from examples.schemas import DepartmentOut


    class DepartmentViewSet(viewsets.ModelViewSet):
        model = Department
        default_response_body = DepartmentOut # Optional

        # Basic usage: Retrieve a department by id
        # Endpoint: GET /{id}/
        retrieve_department = views.RetrieveModelView(
            response_body=DepartmentOut
        )

        # Simplified usage: Inherit from the viewset's default response body
        # Endpoint: GET /{id}/
        retrieve_department = views.RetrieveModelView()

        # Advanced usage: With a custom queryset getter
        # Endpoint: GET /{id}/
        retrieve_department = views.RetrieveModelView(
            response_body=DepartmentOut,
            queryset_getter=lambda id: Department.objects.annotate(
                num_employees=Count("employees")
            ),
        )
    ```

    Note:
        The attribute name (e.g., `retrieve_department`) is flexible and customizable.
        It serves as the name of the route and the operation id in the OpenAPI schema.
    """

    def __init__(
        self,
        path: str = "/{id}",
        response_body: Optional[Type[Schema]] = None,
        queryset_getter: Optional[Callable[[Any], QuerySet]] = None,
        decorators: Optional[List[Callable]] = None,
        router_kwargs: Optional[Dict] = None,
    ) -> None:
        super().__init__(
            method=HTTPMethod.GET,
            path=path,
            query_parameters=None,
            request_body=None,
            response_body=response_body,
            response_status=HTTPStatus.OK,
            decorators=decorators,
            router_kwargs=router_kwargs,
        )

        PathValidator.validate(path=path, allow_no_parameters=False)
        QuerySetGetterValidator.validate(queryset_getter=queryset_getter, path=path)

        self.queryset_getter = queryset_getter

    def build_view(self) -> Callable:
        id_field_type = self.infer_id_field_type()

        def view(request: HttpRequest, id: id_field_type):
            return self.response_status, self.retrieve_model(request=request, id=id)

        return view

    def retrieve_model(self, request: HttpRequest, id: Any):
        if self.queryset_getter:
            queryset = self.queryset_getter(id)
        else:
            queryset = self.model_viewset_class.model.objects.get_queryset()

        return queryset.get(pk=id)

    def _inherit_model_viewset_class_attributes(self) -> None:
        if self.response_body is None:
            self.response_body = self.model_viewset_class.default_response_body
