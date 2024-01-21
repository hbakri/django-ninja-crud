from http import HTTPStatus
from typing import Any, Callable, Dict, List, Optional, Type, Union

from django.db.models import Model
from django.http import HttpRequest
from ninja import Schema

from ninja_crud.views.abstract_model_view import AbstractModelView
from ninja_crud.views.enums import HTTPMethod
from ninja_crud.views.helpers import utils
from ninja_crud.views.validators.model_factory_validator import ModelFactoryValidator
from ninja_crud.views.validators.path_validator import PathValidator


class CreateModelView(AbstractModelView):
    """
    A view class that handles creating a model instance, allowing customization
    through a model factory and pre- and post-save hooks and also supports decorators.

    Args:
        path (str, optional): Path for the view. Defaults to "/". Can include a
            "{id}" parameter for a specific model instance.
        request_body (Optional[Type[ninja.Schema]], optional): Schema for
            deserializing the request body. Defaults to None. If not provided,
            inherits from `ModelViewSet`s `default_request_body`.
        response_body (Optional[Type[ninja.Schema]], optional): Schema for
            serializing the response body. Defaults to None. If not provided,
            inherits from `ModelViewSet`s `default_response_body`.
        model_factory (Union[Callable[[], models.Model],
            Callable[[Any], models.Model], None], optional): Factory function for
            creating the model instance. Defaults to None. If `path` has no
            parameters, should have the signature () -> Model. If `path` has a "{id}"
            parameter, (id: Any) -> Model. If not provided, the `model` of the
            `ModelViewSet` will be used.
        pre_save (Optional[Callable[[HttpRequest, Model], None]], optional): Function
            to execute before saving the model instance. Defaults to None.
        post_save (Optional[Callable[[HttpRequest, Model], None]], optional): Function
            to execute after saving the model instance. Defaults to None.
        decorators (Optional[List[Callable]], optional): Decorators for the view.
            Defaults to [].
        router_kwargs (Optional[Dict], optional): Additional router arguments.
            Defaults to {}. Overrides are ignored for 'path', 'methods', and
            'response'.

    Example:
    ```python
    from ninja_crud import views, viewsets

    from examples.models import Department, Employee
    from examples.schemas import DepartmentIn, DepartmentOut, EmployeeIn, EmployeeOut


    class DepartmentViewSet(viewsets.ModelViewSet):
        model = Department
        default_request_body = DepartmentIn # Optional
        default_response_body = DepartmentOut # Optional

        # Basic usage: Create a department
        # Endpoint: POST /
        create_department = views.CreateModelView(
            request_body=DepartmentIn,
            response_body=DepartmentOut,
        )

        # Simplified usage: Inherit default request/response bodies from ModelViewSet
        # Endpoint: POST /
        create_department = views.CreateModelView()

        # Advanced usage: Create an employee for a department
        # Endpoint: POST /{id}/employees/
        create_employee = views.CreateModelView(
            path="/{id}/employees/",
            request_body=EmployeeIn,
            response_body=EmployeeOut,
            model_factory=lambda id: Employee(department_id=id),
        )
    ```

    Note:
        The attribute name (e.g., `create_department`) is flexible and customizable.
        It serves as the name of the route and the operation id in the OpenAPI schema.
    """

    def __init__(
        self,
        path: str = "/",
        request_body: Optional[Type[Schema]] = None,
        response_body: Optional[Type[Schema]] = None,
        model_factory: Union[Callable[[], Model], Callable[[Any], Model], None] = None,
        pre_save: Optional[Callable[[HttpRequest, Model], None]] = None,
        post_save: Optional[Callable[[HttpRequest, Model], None]] = None,
        decorators: Optional[List[Callable]] = None,
        router_kwargs: Optional[Dict] = None,
    ) -> None:
        super().__init__(
            method=HTTPMethod.POST,
            path=path,
            query_parameters=None,
            request_body=request_body,
            response_body=response_body,
            response_status=HTTPStatus.CREATED,
            decorators=decorators,
            router_kwargs=router_kwargs,
        )

        PathValidator.validate(path=path, allow_no_parameters=True)
        ModelFactoryValidator.validate(model_factory=model_factory, path=path)

        self.model_factory = model_factory
        self.pre_save = pre_save
        self.post_save = post_save

    def build_view(self) -> Callable:
        if "{id}" in self.path:
            return self._build_detail_view()
        else:
            return self._build_collection_view()

    def _build_detail_view(self) -> Callable:
        model_class = self.model_viewset_class.model
        request_body_schema_class = self.request_body

        def detail_view(
            request: HttpRequest,
            id: utils.get_id_type(model_class),
            request_body: request_body_schema_class,
        ):
            if not model_class.objects.filter(pk=id).exists():
                raise model_class.DoesNotExist(
                    f"{model_class.__name__} with pk '{id}' does not exist."
                )

            return self.response_status, self.create_model(
                request=request, id=id, request_body=request_body
            )

        return detail_view

    def _build_collection_view(self) -> Callable:
        request_body_schema_class = self.request_body

        def collection_view(
            request: HttpRequest, request_body: request_body_schema_class
        ):
            return self.response_status, self.create_model(
                request=request, id=None, request_body=request_body
            )

        return collection_view

    def create_model(
        self,
        request: HttpRequest,
        id: Optional[Any],
        request_body: Schema,
    ) -> Model:
        if self.model_factory:
            args = [id] if "{id}" in self.path else []
            instance = self.model_factory(*args)
        else:
            instance = self.model_viewset_class.model()

        for field, value in request_body.dict(exclude_unset=True).items():
            setattr(instance, field, value)

        if self.pre_save:
            self.pre_save(request, instance)

        instance.full_clean()
        instance.save()

        if self.post_save:
            self.post_save(request, instance)

        return instance

    def _inherit_model_viewset_class_attributes(self) -> None:
        if self.request_body is None:
            self.request_body = self.model_viewset_class.default_request_body
        if self.response_body is None:
            self.response_body = self.model_viewset_class.default_response_body
