import copy
from http import HTTPStatus
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Type

from django.db.models import Model
from django.http import HttpRequest
from ninja import Schema

from ninja_crud.views.abstract_model_view import AbstractModelView
from ninja_crud.views.enums import HTTPMethod
from ninja_crud.views.helpers import utils
from ninja_crud.views.helpers.types import UpdateHook
from ninja_crud.views.validators.http_method_validator import HTTPMethodValidator
from ninja_crud.views.validators.path_validator import PathValidator

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
        # PUT /{id}/
        update_department = views.UpdateModelView(input_schema=DepartmentIn, response_schema=DepartmentOut)
    ```

    Note:
        The attribute name (e.g., `update_department`) is flexible and customizable.
        It serves as the name of the route and the operation id in the OpenAPI schema.
    """

    def __init__(
        self,
        input_schema: Optional[Type[Schema]] = None,
        response_schema: Optional[Type[Schema]] = None,
        pre_save: Optional[UpdateHook] = None,
        post_save: Optional[UpdateHook] = None,
        method: HTTPMethod = HTTPMethod.PUT,
        path: str = "/{id}",
        decorators: Optional[List[Callable]] = None,
        router_kwargs: Optional[dict] = None,
    ) -> None:
        """
        Initializes the UpdateModelView.

        Args:
            input_schema (Optional[Type[Schema]], optional): The schema used to deserialize the payload.
                Defaults to None. If not provided, the `default_input_schema` of the `ModelViewSet` will be used.
            response_schema (Optional[Type[Schema]], optional): The schema used to serialize the updated instance.
                Defaults to None. If not provided, the `default_response_schema` of the `ModelViewSet` will be used.
            pre_save (Optional[UpdateHook], optional): A function that is called before saving the instance.
                Defaults to None.

                The function should have the signature:
                - (request: HttpRequest, old_instance: Model, new_instance: Model) -> None

                If not provided, the function will be a no-op.
            post_save (Optional[UpdateHook], optional): A function that is called after saving the instance.
                Defaults to None.

                The function should have the signature:
                - (request: HttpRequest, old_instance: Model, new_instance: Model) -> None

                If not provided, the function will be a no-op.
            method (HTTPMethod, optional): The HTTP method for the view. Defaults to HTTPMethod.PUT.
            path (str, optional): The path to use for the view. Defaults to "/{id}". Must include a "{id}" parameter.
            decorators (Optional[List[Callable]], optional): A list of decorators to apply to the view. Defaults to [].
            router_kwargs (Optional[dict], optional): Additional arguments to pass to the router. Defaults to {}.
                Overrides are allowed for most arguments except 'path', 'methods', and 'response'. If any of these
                arguments are provided, a warning will be logged and the override will be ignored.
        """
        super().__init__(
            method=method,
            path=path,
            filter_schema=None,
            input_schema=input_schema,
            response_schema=response_schema,
            decorators=decorators,
            router_kwargs=router_kwargs,
        )

        HTTPMethodValidator.validate(
            method=method, choices=[HTTPMethod.PUT, HTTPMethod.PATCH]
        )
        PathValidator.validate(path=path, allow_no_parameters=False)

        self.pre_save = pre_save
        self.post_save = post_save

    def build_view(self, model_class: Type[Model]) -> Callable:
        input_schema = self.input_schema

        def view(
            request: HttpRequest,
            id: utils.get_id_type(model_class),
            payload: input_schema,
        ):
            return HTTPStatus.OK, self.update_model(
                request=request, id=id, payload=payload, model_class=model_class
            )

        return view

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

    def get_response(self) -> dict:
        """
        Provides a mapping of HTTP status codes to response schemas for the update view.

        This response schema is used in API documentation to describe the response body for this view.
        The response schema is critical and cannot be overridden using `router_kwargs`. Any overrides
        will be ignored.

        Returns:
            dict: A mapping of HTTP status codes to response schemas for the update view.
                Defaults to {200: self.response_schema}. For example, for a model "Department", the response
                schema would be {200: DepartmentOut}.
        """
        return {HTTPStatus.OK: self.response_schema}

    def bind_to_viewset(
        self, viewset_class: Type["ModelViewSet"], model_view_name: str
    ) -> None:
        super().bind_to_viewset(viewset_class, model_view_name)
        self.bind_default_input_schema(viewset_class, model_view_name)
        self.bind_default_response_schema(viewset_class, model_view_name)
