import copy
from http import HTTPStatus
from typing import Callable, List, Optional, Type

from django.db.models import Model
from django.http import HttpRequest
from ninja import Router, Schema

from ninja_crud.views import utils
from ninja_crud.views.abstract import AbstractModelView
from ninja_crud.views.enums import HTTPMethod
from ninja_crud.views.types import UpdateSaveHook


class UpdateModelView(AbstractModelView):
    """
    A view class that handles updating a specific instance of a model.
    It allows customization through pre- and post-save hooks and also supports decorators.

    Example:
    ```python
    from ninja_crud.views import ModelViewSet, UpdateModelView
    from example.models import Department
    from example.schemas import DepartmentIn, DepartmentOut

    class DepartmentViewSet(ModelViewSet):
        model_class = Department

        # Usage: Update a department by id
        # PUT /departments/{id}/
        update = UpdateModelView(input_schema=DepartmentIn, output_schema=DepartmentOut)
    ```
    """

    def __init__(
        self,
        input_schema: Type[Schema],
        output_schema: Type[Schema],
        pre_save: Optional[UpdateSaveHook] = None,
        post_save: Optional[UpdateSaveHook] = None,
        method: HTTPMethod = HTTPMethod.PUT,
        path: Optional[str] = None,
        decorators: Optional[List[Callable]] = None,
        router_kwargs: Optional[dict] = None,
    ) -> None:
        """
        Initializes the UpdateModelView.

        Args:
            input_schema (Type[Schema]): The schema used to deserialize the payload.
            output_schema (Type[Schema]): The schema used to serialize the updated instance.
            pre_save (Optional[UpdateSaveHook], optional): A function that is called before saving the instance. Defaults to None.

                The function should have the signature:
                - (request: HttpRequest, old_instance: Model, new_instance: Model) -> None

                If not provided, the function will be a no-op.
            post_save (Optional[UpdateSaveHook], optional): A function that is called after saving the instance. Defaults to None.

                The function should have the signature:
                - (request: HttpRequest, old_instance: Model, new_instance: Model) -> None

                If not provided, the function will be a no-op.
            method (HTTPMethod, optional): The HTTP method for the view. Defaults to HTTPMethod.PUT.
            path (Optional[str], optional): The path to use for the view. Defaults to "/{id}".
            decorators (Optional[List[Callable]], optional): A list of decorators to apply to the view. Defaults to [].
            router_kwargs (Optional[dict], optional): Additional arguments to pass to the router. Defaults to {}.
        """
        if path is None:
            path = self._get_default_path()
        super().__init__(
            method=method,
            path=path,
            detail=True,
            decorators=decorators,
            router_kwargs=router_kwargs,
        )
        if method.value not in [HTTPMethod.PUT.value, HTTPMethod.PATCH.value]:
            raise ValueError(
                f"Expected 'method' to be either PUT or PATCH, but found {method}."
            )
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.pre_save = pre_save
        self.post_save = post_save

    def register_route(self, router: Router, model_class: Type[Model]) -> None:
        input_schema = self.input_schema

        @router.api_operation(
            **self._sanitize_and_merge_router_kwargs(
                default_router_kwargs=self._get_default_router_kwargs(model_class),
                custom_router_kwargs=self.router_kwargs,
            ),
        )
        @utils.merge_decorators(self.decorators)
        def update_model(
            request: HttpRequest,
            id: utils.get_id_type(model_class),
            payload: input_schema,
        ):
            new_instance = model_class.objects.get(pk=id)

            old_instance = None
            if self.pre_save is not None or self.post_save is not None:
                old_instance = copy.deepcopy(new_instance)

            for field, value in payload.dict(exclude_unset=True).items():
                setattr(new_instance, field, value)

            if self.pre_save is not None:
                self.pre_save(request, old_instance, new_instance)

            new_instance.full_clean()
            new_instance.save()

            if self.post_save is not None:
                self.post_save(request, old_instance, new_instance)

            return HTTPStatus.OK, new_instance

    @staticmethod
    def _get_default_path() -> str:
        return "/{id}"

    def _get_default_router_kwargs(self, model_class: Type[Model]) -> dict:
        return dict(
            methods=[self.method.value],
            path=self.path,
            response={HTTPStatus.OK: self.output_schema},
            operation_id=self._get_operation_id(model_class),
            summary=self._get_summary(model_class),
        )

    @staticmethod
    def _get_operation_id(model_class: Type[Model]) -> str:
        return f"update_{utils.to_snake_case(model_class.__name__)}"

    @staticmethod
    def _get_summary(model_class: Type[Model]) -> str:
        return f"Update {model_class.__name__}"
