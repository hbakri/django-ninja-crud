from http import HTTPStatus
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Type

from django.db.models import Model
from django.http import HttpRequest
from ninja import Schema

from ninja_crud.views.abstract_model_view import AbstractModelView
from ninja_crud.views.enums import HTTPMethod
from ninja_crud.views.helpers import utils
from ninja_crud.views.helpers.types import (
    CreateHook,
    ModelFactory,
)
from ninja_crud.views.validators.model_factory_validator import ModelFactoryValidator
from ninja_crud.views.validators.path_validator import PathValidator

if TYPE_CHECKING:  # pragma: no cover
    from ninja_crud.viewsets import ModelViewSet


class CreateModelView(AbstractModelView):
    """
    A view class that handles creating instances of a model.
    It allows customization through an model factory, pre- and post-save hooks,
    and also supports decorators.

    Example:
    ```python
    from ninja_crud import views, viewsets

    from examples.models import Department, Employee
    from examples.schemas import DepartmentIn, DepartmentOut, EmployeeIn, EmployeeOut

    class DepartmentViewSet(viewsets.ModelViewSet):
        model = Department

        # Basic usage: Create a department
        # POST /
        create_department = views.CreateModelView(
            input_schema=DepartmentIn,
            output_schema=DepartmentOut
        )

        # Advanced usage: Create an employee for a specific department
        # POST /{id}/employees/
        create_employee = views.CreateModelView(
            path="/{id}/employees/",
            model_factory=lambda id: Employee(department_id=id),
            input_schema=EmployeeIn,
            output_schema=EmployeeOut,
        )
    ```

    Note:
        The attribute name (e.g., `create_department`, `create_employee`) is flexible and customizable.
        It serves as the name of the route and the operation id in the OpenAPI schema.
    """

    def __init__(
        self,
        input_schema: Optional[Type[Schema]] = None,
        output_schema: Optional[Type[Schema]] = None,
        model_factory: Optional[ModelFactory] = None,
        pre_save: Optional[CreateHook] = None,
        post_save: Optional[CreateHook] = None,
        path: str = "/",
        decorators: Optional[List[Callable]] = None,
        router_kwargs: Optional[dict] = None,
    ) -> None:
        """
        Initializes the CreateModelView.

        Args:
            input_schema (Optional[Type[Schema]], optional): The schema used to deserialize the payload.
                Defaults to None. If not provided, the `default_input_schema` of the `ModelViewSet` will be used.
            output_schema (Optional[Type[Schema]], optional): The schema used to serialize the created instance.
                Defaults to None. If not provided, the `default_output_schema` of the `ModelViewSet` will be used.
            model_factory (Optional[ModelFactory], optional): A function that returns a new instance of a model.
                Defaults to None.

                The function should have one of the following signatures:
                - If `path` has no parameters: () -> Model
                - If `path` has a "{id}" parameter: (id: Any) -> Model

                If not provided, the `model` specified in the `ModelViewSet` will be used.
            pre_save (Optional[CreateHook], optional): A function that is called before saving the instance.
                Defaults to None.

                The function should have one of the following signatures:
                - If `path` has no parameters: (request: HttpRequest, instance: Model) -> None
                - If `path` has a "{id}" parameter: (request: HttpRequest, id: Any, instance: Model) -> None

                If not provided, the function will be a no-op.
            post_save (Optional[CreateHook], optional): A function that is called after saving the instance.
                Defaults to None.

                The function should have one of the following signatures:
                - If `path` has no parameters: (request: HttpRequest, instance: Model) -> None
                - If `path` has a "{id}" parameter: (request: HttpRequest, id: Any, instance: Model) -> None

                If not provided, the function will be a no-op.
            path (str, optional): The path to use for the view. Defaults to "/". The path may include a "{id}"
                parameter to indicate that the view is for a specific instance of the model.
            decorators (Optional[List[Callable]], optional): A list of decorators to apply to the view. Defaults to [].
            router_kwargs (Optional[dict], optional): Additional arguments to pass to the router. Defaults to {}.
                Overrides are allowed for most arguments except 'path', 'methods', and 'response'. If any of these
                arguments are provided, a warning will be logged and the override will be ignored.
        """
        super().__init__(
            method=HTTPMethod.POST,
            path=path,
            decorators=decorators,
            router_kwargs=router_kwargs,
        )

        PathValidator.validate(path=path, allow_no_parameters=True)
        ModelFactoryValidator.validate(model_factory=model_factory, path=path)

        self.input_schema = input_schema
        self.output_schema = output_schema
        self.model_factory = model_factory
        self.pre_save = pre_save
        self.post_save = post_save

    def build_view(self, model_class: Type[Model]) -> Callable:
        if "{id}" in self.path:
            return self._build_detail_view(model_class)
        else:
            return self._build_collection_view(model_class)

    def _build_detail_view(self, model_class: Type[Model]) -> Callable:
        input_schema = self.input_schema

        def detail_view(
            request: HttpRequest,
            id: utils.get_id_type(model_class),
            payload: input_schema,
        ):
            if not model_class.objects.filter(pk=id).exists():
                raise model_class.DoesNotExist(
                    f"{model_class.__name__} with pk '{id}' does not exist."
                )

            return HTTPStatus.CREATED, self.create_model(
                request=request, id=id, payload=payload, model_class=model_class
            )

        return detail_view

    def _build_collection_view(self, model_class: Type[Model]) -> Callable:
        input_schema = self.input_schema

        def collection_view(request: HttpRequest, payload: input_schema):
            return HTTPStatus.CREATED, self.create_model(
                request=request, id=None, payload=payload, model_class=model_class
            )

        return collection_view

    def create_model(
        self,
        request: HttpRequest,
        id: Optional[Any],
        payload: Schema,
        model_class: Type[Model],
    ) -> Model:
        if self.model_factory:
            args = [id] if "{id}" in self.path else []
            instance = self.model_factory(*args)
        else:
            instance = model_class()

        for field, value in payload.dict(exclude_unset=True).items():
            setattr(instance, field, value)

        if self.pre_save:
            args = (
                (request, id, instance) if "{id}" in self.path else (request, instance)
            )
            self.pre_save(*args)

        instance.full_clean()
        instance.save()

        if self.post_save:
            args = (
                (request, id, instance) if "{id}" in self.path else (request, instance)
            )
            self.post_save(*args)

        return instance

    def get_response(self) -> dict:
        """
        Provides a mapping of HTTP status codes to response schemas for the create view.

        This response schema is used in API documentation to describe the response body for this view.
        The response schema is critical and cannot be overridden using `router_kwargs`. Any overrides
        will be ignored.

        Returns:
            dict: A mapping of HTTP status codes to response schemas for the create view.
                Defaults to {201: self.output_schema}. For example, for a model "Department", the response
                schema would be {201: DepartmentOut}.
        """
        return {HTTPStatus.CREATED: self.output_schema}

    def bind_to_viewset(
        self, viewset_class: Type["ModelViewSet"], model_view_name: str
    ) -> None:
        super().bind_to_viewset(viewset_class, model_view_name)
        self.bind_default_value(
            viewset_class=viewset_class,
            model_view_name=model_view_name,
            attribute_name="output_schema",
            default_attribute_name="default_output_schema",
        )
        self.bind_default_value(
            viewset_class=viewset_class,
            model_view_name=model_view_name,
            attribute_name="input_schema",
            default_attribute_name="default_input_schema",
        )
