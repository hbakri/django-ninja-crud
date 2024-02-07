from http import HTTPStatus
from typing import Any, Callable, Dict, List, Optional, Type, Union

from django.db.models import Model
from django.http import HttpRequest
from ninja import Schema

from ninja_crud.views.abstract_model_view import AbstractModelView
from ninja_crud.views.enums import HTTPMethod
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

        # Simplified usage: Inherit from the viewset's default request/response bodies
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

    def handle_request(
        self,
        request: HttpRequest,
        path_parameters: Optional[Schema],
        query_parameters: Optional[Schema],
        request_body: Optional[Schema],
    ) -> Model:
        if path_parameters:
            self.model_viewset_class.model.objects.get(**path_parameters.dict())

        if self.model_factory:
            model_factory_kwargs = path_parameters.dict() if path_parameters else {}
            instance = self.model_factory(**model_factory_kwargs)
        else:
            instance = self.model_viewset_class.model()

        if request_body:
            for field, value in request_body.dict().items():
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
