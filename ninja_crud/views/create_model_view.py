from http import HTTPStatus
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Type, Union

from django.db.models import Model
from django.http import HttpRequest
from ninja import Router, Schema

from ninja_crud.views.abstract_model_view import AbstractModelView
from ninja_crud.views.enums import HTTPMethod
from ninja_crud.views.helpers import utils
from ninja_crud.views.helpers.types import (
    CollectionModelFactory,
    CreateCollectionSaveHook,
    CreateDetailSaveHook,
    DetailModelFactory,
)
from ninja_crud.views.validators.model_factory_validator import ModelFactoryValidator

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
        # POST /departments/
        create_department_view = views.CreateModelView(
            input_schema=DepartmentIn,
            output_schema=DepartmentOut
        )

        # Advanced usage: Create an employee for a specific department
        # POST /departments/{id}/employees/
        create_employee_view = views.CreateModelView(
            detail=True,
            model_factory=lambda id: Employee(department_id=id),
            input_schema=EmployeeIn,
            output_schema=EmployeeOut,
        )
    ```
    """

    def __init__(
        self,
        input_schema: Optional[Type[Schema]] = None,
        output_schema: Optional[Type[Schema]] = None,
        detail: bool = False,
        model_factory: Union[DetailModelFactory, CollectionModelFactory, None] = None,
        pre_save: Union[CreateDetailSaveHook, CreateCollectionSaveHook, None] = None,
        post_save: Union[CreateDetailSaveHook, CreateCollectionSaveHook, None] = None,
        path: Optional[str] = None,
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
            detail (bool, optional): Whether the view is a detail or collection view. Defaults to False.

                If set to True, `model_factory` must be provided.
            model_factory (Union[DetailModelFactory, CollectionModelFactory, None], optional): A function
                that returns a new instance of a model. Defaults to None.

                The function should have one of the following signatures:
                - For `detail=False`: () -> Model
                - For `detail=True`: (id: Any) -> Model

                If not provided, the `model` specified in the `ModelViewSet` will be used.
            pre_save (Union[CreateDetailSaveHook, CreateCollectionSaveHook, None], optional): A function that
                is called before saving the instance. Defaults to None.

                The function should have one of the following signatures:
                - For `detail=False`: (request: HttpRequest, instance: Model) -> None
                - For `detail=True`: (request: HttpRequest, id: Any, instance: Model) -> None

                If not provided, the function will be a no-op.
            post_save (Union[CreateDetailSaveHook, CreateCollectionSaveHook, None], optional): A function that
                is called after saving the instance. Defaults to None.

                The function should have one of the following signatures:
                - For `detail=False`: (request: HttpRequest, instance: Model) -> None
                - For `detail=True`: (request: HttpRequest, id: Any, instance: Model) -> None

                If not provided, the function will be a no-op.
            path (Optional[str], optional): The path to use for the view. Defaults to:
                - For `detail=False`: "/"
                - For `detail=True`: "/{id}/{related_model_name_plural_to_snake_case}/"

                Where `related_model_name_plural_to_snake_case` refers to the plural form of the related model's name,
                converted to snake_case. For example, for a related model "ItemDetail", the path might look like
                "/{id}/item_details/". This format is particularly useful when querying related entities or
                sub-resources of a main resource.
            decorators (Optional[List[Callable]], optional): A list of decorators to apply to the view. Defaults to [].
            router_kwargs (Optional[dict], optional): Additional arguments to pass to the router. Defaults to {}.
                Overrides are allowed for most arguments except 'path', 'methods', and 'response'. If any of these
                arguments are provided, a warning will be logged and the override will be ignored.
        """
        if detail and model_factory is None:
            raise ValueError(
                "Expected 'model_factory' when 'detail=True', but found None."
            )
        ModelFactoryValidator.validate(model_factory, detail)
        model_factory_class: Optional[Type[Model]] = (
            model_factory(None).__class__ if detail else None
        )

        if path is None:
            path = self._get_default_path(
                detail=detail, model_class=model_factory_class
            )
        super().__init__(
            method=HTTPMethod.POST,
            path=path,
            detail=detail,
            decorators=decorators,
            router_kwargs=router_kwargs,
        )

        self.input_schema = input_schema
        self.output_schema = output_schema
        self.model_factory = model_factory
        self.pre_save = pre_save
        self.post_save = post_save
        self._related_model_class = model_factory_class

    def register_route(self, router: Router, model_class: Type[Model]) -> None:
        if self.detail:
            self._register_detail_route(router, model_class)
        else:
            self._register_collection_route(router, model_class)

    def _register_detail_route(self, router: Router, model_class: Type[Model]) -> None:
        input_schema = self.input_schema

        @self.configure_route(router=router, model_class=model_class)
        def create_model(
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

    def _register_collection_route(
        self, router: Router, model_class: Type[Model]
    ) -> None:
        input_schema = self.input_schema

        @self.configure_route(router=router, model_class=model_class)
        def create_model(request: HttpRequest, payload: input_schema):
            return HTTPStatus.CREATED, self.create_model(
                request=request, id=None, payload=payload, model_class=model_class
            )

    def create_model(
        self,
        request: HttpRequest,
        id: Optional[Any],
        payload: Schema,
        model_class: Type[Model],
    ) -> Model:
        if self.model_factory:
            args = [id] if self.detail else []
            instance = self.model_factory(*args)
        else:
            instance = model_class()

        for field, value in payload.dict(exclude_unset=True).items():
            setattr(instance, field, value)

        if self.pre_save:
            args = (request, id, instance) if self.detail else (request, instance)
            self.pre_save(*args)

        instance.full_clean()
        instance.save()

        if self.post_save:
            args = (request, id, instance) if self.detail else (request, instance)
            self.post_save(*args)

        return instance

    @staticmethod
    def _get_default_path(detail: bool, model_class: Type[Model]) -> str:
        if detail:
            related_model_name = utils.to_snake_case(model_class.__name__)
            return f"/{{id}}/{related_model_name}s/"
        else:
            return "/"

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

    def get_operation_id(self, model_class: Type[Model]) -> str:
        """
        Provides an operation ID for the create view.

        This operation ID is used in API documentation to uniquely identify this view.
        It can be overriden using the `router_kwargs`.

        Args:
            model_class (Type[Model]): The Django model class associated with this view.

        Returns:
            str: The operation ID for the create view. Defaults to:
                - For `detail=False`: "create_{model_name_to_snake_case}". For example, for a model "Department",
                    the operation ID would be "create_department".
                - For `detail=True`: "create_{model_name_to_snake_case}_{related_model_name_to_snake_case}". For
                    example, for a model "Department" and a related model "Item", the operation ID would be
                    "create_department_item".
        """
        model_name = utils.to_snake_case(model_class.__name__)
        if self.detail:
            related_model_name = utils.to_snake_case(self._related_model_class.__name__)
            return f"create_{model_name}_{related_model_name}"
        else:
            return f"create_{model_name}"

    def get_summary(self, model_class: Type[Model]) -> str:
        """
        Provides a summary description for the create view.

        This summary is used in API documentation to give a brief description of what this view does.
        It can be overriden using the `router_kwargs`.

        Args:
            model_class (Type[Model]): The Django model class associated with this view.

        Returns:
            str: The summary description for the create view. Defaults to:
                - For `detail=False`: "Create {model_name}". For example, for a model "Department", the summary
                    would be "Create Department".
                - For `detail=True`: "Create {related_model_name} related to a {model_name}". For example, for a
                    model "Department" and a related model "Item", the summary would be "Create Item related to a
                    Department".
        """
        verbose_model_name = model_class._meta.verbose_name
        if self.detail:
            verbose_model_name = model_class._meta.verbose_name
            verbose_related_model_name = self._related_model_class._meta.verbose_name
            return (
                f"Create {verbose_related_model_name} related to a {verbose_model_name}"
            )
        else:
            return f"Create {verbose_model_name}"

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
