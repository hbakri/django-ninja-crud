import copy
from http import HTTPStatus
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Type

from django.db.models import Model
from django.http import HttpRequest
from ninja import Router, Schema

from ninja_crud.views.abstract_model_view import AbstractModelView
from ninja_crud.views.enums import HTTPMethod
from ninja_crud.views.helpers import utils
from ninja_crud.views.helpers.types import UpdateSaveHook

if TYPE_CHECKING:  # pragma: no cover
    from ninja_crud.viewsets import ModelViewSet


class UpdateModelView(AbstractModelView):
    """
    A view class that handles updating a specific instance of a model.
    It allows customization through pre- and post-save hooks and also supports decorators.

    Example:
    ```python
    from ninja_crud import views, viewsets

    from examples.models import Department
    from examples.schemas import DepartmentIn, DepartmentOut

    class DepartmentViewSet(viewsets.ModelViewSet):
        model = Department

        # Usage: Update a department by id
        # PUT /departments/{id}/
        update_department_view = views.UpdateModelView(input_schema=DepartmentIn, output_schema=DepartmentOut)
    ```
    """

    def __init__(
        self,
        input_schema: Optional[Type[Schema]] = None,
        output_schema: Optional[Type[Schema]] = None,
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
            input_schema (Optional[Type[Schema]], optional): The schema used to deserialize the payload.
                Defaults to None. If not provided, the `default_input_schema` of the `ModelViewSet` will be used.
            output_schema (Optional[Type[Schema]], optional): The schema used to serialize the updated instance.
                Defaults to None. If not provided, the `default_output_schema` of the `ModelViewSet` will be used.
            pre_save (Optional[UpdateSaveHook], optional): A function that is called before saving the instance.
                Defaults to None.

                The function should have the signature:
                - (request: HttpRequest, old_instance: Model, new_instance: Model) -> None

                If not provided, the function will be a no-op.
            post_save (Optional[UpdateSaveHook], optional): A function that is called after saving the instance.
                Defaults to None.

                The function should have the signature:
                - (request: HttpRequest, old_instance: Model, new_instance: Model) -> None

                If not provided, the function will be a no-op.
            method (HTTPMethod, optional): The HTTP method for the view. Defaults to HTTPMethod.PUT.
            path (Optional[str], optional): The path to use for the view. Defaults to "/{id}".
            decorators (Optional[List[Callable]], optional): A list of decorators to apply to the view. Defaults to [].
            router_kwargs (Optional[dict], optional): Additional arguments to pass to the router. Defaults to {}.
                Overrides are allowed for most arguments except 'path', 'methods', and 'response'. If any of these
                arguments are provided, a warning will be logged and the override will be ignored.
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

        @self.configure_route(router=router, model_class=model_class)
        def update_model(
            request: HttpRequest,
            id: utils.get_id_type(model_class),
            payload: input_schema,
        ):
            return HTTPStatus.OK, self.update_model(
                request=request, id=id, payload=payload, model_class=model_class
            )

    def update_model(
        self, request: HttpRequest, id: Any, payload: Schema, model_class: Type[Model]
    ) -> Model:
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

        return new_instance

    @staticmethod
    def _get_default_path() -> str:
        return "/{id}"

    def get_response(self) -> dict:
        """
        Provides a mapping of HTTP status codes to response schemas for the update view.

        This response schema is used in API documentation to describe the response body for this view.
        The response schema is critical and cannot be overridden using `router_kwargs`. Any overrides
        will be ignored.

        Returns:
            dict: A mapping of HTTP status codes to response schemas for the update view.
                Defaults to {200: self.output_schema}. For example, for a model "Department", the response
                schema would be {200: DepartmentOut}.
        """
        return {HTTPStatus.OK: self.output_schema}

    def get_operation_id(self, model_class: Type[Model]) -> str:
        """
        Provides an operation ID for the update view.

        This operation ID is used in API documentation to uniquely identify this view.
        It can be overriden using the `router_kwargs`.

        Args:
            model_class (Type[Model]): The Django model class associated with this view.

        Returns:
            str: The operation ID for the update view. Defaults to "update_{model_name_to_snake_case}". For
                example, for a model "Department", the operation ID would be "update_department".
        """
        return f"update_{utils.to_snake_case(model_class.__name__)}"

    def get_summary(self, model_class: Type[Model]) -> str:
        """
        Provides a summary description for the update view.

        This summary is used in API documentation to give a brief description of what this view does.
        It can be overriden using the `router_kwargs`.

        Args:
            model_class (Type[Model]): The Django model class associated with this view.

        Returns:
            str: The summary description for the update view. Defaults to "Update {model_name}". For
                example, for a model "Department", the summary would be "Update Department".
        """
        return f"Update {model_class.__name__}"

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
