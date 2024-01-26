import copy
from http import HTTPStatus
from typing import Any, Callable, Dict, List, Optional, Type

from django.db.models import Model
from django.http import HttpRequest
from ninja import Schema

from ninja_crud.views.abstract_model_view import AbstractModelView
from ninja_crud.views.enums import HTTPMethod
from ninja_crud.views.validators.http_method_validator import HTTPMethodValidator
from ninja_crud.views.validators.path_validator import PathValidator


class UpdateModelView(AbstractModelView):
    """
    A view class that handles updating a model instance, allowing customization
    through pre- and post-save hooks and supporting decorators.

    Args:
        method (HTTPMethod, optional): HTTP method for the view. Defaults to
            HTTPMethod.PUT. Can be HTTPMethod.PATCH.
        path (str, optional): Path for the view. Defaults to "/{id}". Should
            include a "{id}" parameter for a specific model instance.
        request_body (Optional[Type[ninja.Schema]], optional): Schema for
            deserializing the request body. Defaults to None. If not provided,
            inherits from `ModelViewSet`s `default_request_body`.
        response_body (Optional[Type[ninja.Schema]], optional): Schema for
            serializing the response body. Defaults to None. If not provided,
            inherits from `ModelViewSet`s `default_response_body`.
        pre_save (Optional[Callable[[HttpRequest, Model, Model], None]], optional):
            Function to execute before saving the model instance. Defaults to None.
            Should have the signature (request: HttpRequest, old_instance: Model,
            new_instance: Model) -> None.
        post_save (Optional[Callable[[HttpRequest, Model, Model], None]], optional):
            Function to execute after saving the model instance. Defaults to None.
            Should have the signature (request: HttpRequest, old_instance: Model,
            new_instance: Model) -> None.
        decorators (Optional[List[Callable]], optional): Decorators for the view.
            Defaults to [].
        router_kwargs (Optional[Dict], optional): Additional router arguments.
            Defaults to {}. Overrides are ignored for 'path', 'methods', and
            'response'.

    Example:
    ```python
    from django.http import HttpRequest
    from ninja_crud import views, viewsets

    from examples.models import Department
    from examples.schemas import DepartmentIn, DepartmentOut


    class DepartmentViewSet(viewsets.ModelViewSet):
        model = Department
        default_request_body = DepartmentIn # Optional
        default_response_body = DepartmentOut # Optional

        # Basic usage: Update a department
        # Endpoint: PUT /{id}/
        update_department = views.UpdateModelView(
            request_body=DepartmentIn,
            response_body=DepartmentOut,
        )

        # Simplified usage: Inherit from the viewset's default request/response bodies
        # Endpoint: PUT /{id}/
        update_department = views.UpdateModelView()

        # Advanced usage: With pre- and post-save hooks
        # Endpoint: PUT /{id}/
        @staticmethod
        def pre_save(request: HttpRequest, old_instance: Department, new_instance: Department):
            pass

        @staticmethod
        def post_save(request: HttpRequest, old_instance: Department, new_instance: Department):
            pass

        update_department = views.UpdateModelView(
            request_body=DepartmentIn,
            response_body=DepartmentOut,
            pre_save=pre_save,
            post_save=post_save,
        )
    ```

    Note:
        The attribute name (e.g., `update_department`) is flexible and customizable.
        It serves as the name of the route and the operation id in the OpenAPI schema.
    """

    def __init__(
        self,
        method: HTTPMethod = HTTPMethod.PUT,
        path: str = "/{id}",
        request_body: Optional[Type[Schema]] = None,
        response_body: Optional[Type[Schema]] = None,
        pre_save: Optional[Callable[[HttpRequest, Model, Model], None]] = None,
        post_save: Optional[Callable[[HttpRequest, Model, Model], None]] = None,
        decorators: Optional[List[Callable]] = None,
        router_kwargs: Optional[Dict] = None,
    ) -> None:
        super().__init__(
            method=method,
            path=path,
            query_parameters=None,
            request_body=request_body,
            response_body=response_body,
            response_status=HTTPStatus.OK,
            decorators=decorators,
            router_kwargs=router_kwargs,
        )

        HTTPMethodValidator.validate(
            method=method, choices=[HTTPMethod.PUT, HTTPMethod.PATCH]
        )
        PathValidator.validate(path=path, allow_no_parameters=False)

        self.pre_save = pre_save
        self.post_save = post_save

    def build_view(self) -> Callable:
        id_field_type = self.infer_id_field_type()
        request_body_schema_class = self.request_body

        def view(
            request: HttpRequest,
            id: id_field_type,
            request_body: request_body_schema_class,
        ):
            return self.response_status, self.update_model(
                request=request, id=id, request_body=request_body
            )

        return view

    def update_model(
        self, request: HttpRequest, id: Any, request_body: Schema
    ) -> Model:
        new_instance = self.model_viewset_class.model.objects.get(pk=id)

        old_instance = None
        if self.pre_save is not None or self.post_save is not None:
            old_instance = copy.deepcopy(new_instance)

        for field, value in request_body.dict(exclude_unset=True).items():
            setattr(new_instance, field, value)

        if self.pre_save is not None:
            self.pre_save(request, old_instance, new_instance)

        new_instance.full_clean()
        new_instance.save()

        if self.post_save is not None:
            self.post_save(request, old_instance, new_instance)

        return new_instance

    def _inherit_model_viewset_class_attributes(self) -> None:
        if self.request_body is None:
            self.request_body = self.model_viewset_class.default_request_body
        if self.response_body is None:
            self.response_body = self.model_viewset_class.default_response_body
