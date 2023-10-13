import functools
from http import HTTPStatus
from typing import Any, Callable, List, Optional, Type, Union

from django.db.models import Model
from django.http import HttpRequest
from ninja import Router, Schema

from ninja_crud.views import utils
from ninja_crud.views.abstract import AbstractModelView
from ninja_crud.views.enums import HTTPMethod
from ninja_crud.views.types import (
    CollectionModelFactory,
    CreateCollectionSaveHook,
    CreateDetailSaveHook,
    DetailModelFactory,
)
from ninja_crud.views.validators.model_factory_validator import ModelFactoryValidator


class CreateModelView(AbstractModelView):
    """
    A view class that handles creating instances of a model.
    It allows customization through an model factory, pre- and post-save hooks,
    and also supports decorators.

    Example:
    ```python
    from ninja_crud.views import ModelViewSet, CreateModelView
    from example.models import Department, Employee
    from example.schemas import DepartmentIn, DepartmentOut, EmployeeIn, EmployeeOut

    class DepartmentViewSet(ModelViewSet):
        model_class = Department

        # Basic usage: Create a department
        # POST /departments/
        create = CreateModelView(
            input_schema=DepartmentIn,
            output_schema=DepartmentOut
        )

        # Advanced usage: Create an employee for a specific department
        # POST /departments/{id}/employees/
        create_employee = CreateModelView(
            detail=True,
            model_factory=lambda id: Employee(department_id=id),
            input_schema=EmployeeIn,
            output_schema=EmployeeOut,
        )
    ```
    """

    def __init__(
        self,
        input_schema: Type[Schema],
        output_schema: Type[Schema],
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
            input_schema (Type[Schema]): The schema used to deserialize the payload.
            output_schema (Type[Schema]): The schema used to serialize the created instance.
            detail (bool, optional): Whether the view is a detail or collection view. Defaults to False.

                If set to True, `model_factory` must be provided.
            model_factory (Union[DetailModelFactory, CollectionModelFactory, None], optional): A function
                that returns a new instance of a model. Defaults to None.

                The function should have one of the following signatures:
                - For `detail=False`: () -> Model
                - For `detail=True`: (id: Any) -> Model

                If not provided, the `model_class` specified in the `ModelViewSet` will be used.
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
        self._related_model = model_factory_class

    def register_route(self, router: Router, model_class: Type[Model]) -> None:
        if self.detail:
            self._register_detail_route(router, model_class)
        else:
            self._register_collection_route(router, model_class)

    def _register_detail_route(self, router: Router, model_class: Type[Model]) -> None:
        input_schema = self.input_schema

        @self._configure_route(router, model_class)
        def create_model(
            request: HttpRequest,
            id: utils.get_id_type(model_class),
            payload: input_schema,
        ):
            if not model_class.objects.filter(pk=id).exists():
                raise model_class.DoesNotExist(
                    f"{model_class.__name__} with pk '{id}' does not exist."
                )

            instance = self._create_model(model_class, id)
            instance = self._save_model(instance, payload, request, id)
            return HTTPStatus.CREATED, instance

    def _register_collection_route(
        self, router: Router, model_class: Type[Model]
    ) -> None:
        input_schema = self.input_schema

        @self._configure_route(router, model_class)
        def create_model(request: HttpRequest, payload: input_schema):
            instance = self._create_model(model_class)
            instance = self._save_model(instance, payload, request)
            return HTTPStatus.CREATED, instance

    def _create_model(
        self, model_class: Type[Model], id: Optional[Any] = None
    ) -> Model:
        if self.model_factory:
            args = [id] if self.detail else []
            return self.model_factory(*args)
        else:
            return model_class()

    def _save_model(
        self,
        instance: Model,
        payload: Schema,
        request: HttpRequest,
        id: Optional[Any] = None,
    ) -> Model:
        for field, value in payload.dict(exclude_unset=True).items():
            setattr(instance, field, value)

        if self.pre_save:
            args = (request, instance) if not id else (request, id, instance)
            self.pre_save(*args)

        instance.full_clean()
        instance.save()

        if self.post_save:
            args = (request, instance) if not id else (request, id, instance)
            self.post_save(*args)

        return instance

    def _configure_route(self, router: Router, model_class: Type[Model]):
        def decorator(route_func):
            @router.api_operation(
                **self._sanitize_and_merge_router_kwargs(
                    default_router_kwargs=self._get_default_router_kwargs(model_class),
                    custom_router_kwargs=self.router_kwargs,
                )
            )
            @utils.merge_decorators(self.decorators)
            @functools.wraps(route_func)
            def wrapped_func(*args, **kwargs):
                return route_func(*args, **kwargs)

            return wrapped_func

        return decorator

    @staticmethod
    def _get_default_path(detail: bool, model_class: Type[Model]) -> str:
        if detail:
            related_model_name = utils.to_snake_case(model_class.__name__)
            return f"/{{id}}/{related_model_name}s/"
        else:
            return "/"

    def _get_default_router_kwargs(self, model_class: Type[Model]) -> dict:
        return dict(
            methods=[self.method.value],
            path=self.path,
            response={HTTPStatus.CREATED: self.output_schema},
            operation_id=self._get_operation_id(model_class),
            summary=self._get_summary(model_class),
        )

    def _get_operation_id(self, model_class: Type[Model]) -> str:
        model_name = utils.to_snake_case(model_class.__name__)
        if self.detail:
            related_model_name = utils.to_snake_case(self._related_model.__name__)
            return f"create_{model_name}_{related_model_name}"
        else:
            return f"create_{model_name}"

    def _get_summary(self, model_class: Type[Model]) -> str:
        verbose_model_name = model_class._meta.verbose_name
        if self.detail:
            verbose_model_name = model_class._meta.verbose_name
            verbose_related_model_name = self._related_model._meta.verbose_name
            return f"Create {verbose_related_model_name} for {verbose_model_name}"
        else:
            return f"Create {verbose_model_name}"
