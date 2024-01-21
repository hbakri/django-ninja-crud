import copy
from http import HTTPStatus
from typing import Any, Callable, List, Optional, Type

from django.db.models import Model
from django.http import HttpRequest
from ninja import Schema

from ninja_crud.views.abstract_model_view import AbstractModelView
from ninja_crud.views.enums import HTTPMethod
from ninja_crud.views.helpers import utils
from ninja_crud.views.helpers.types import UpdateHook
from ninja_crud.views.validators.http_method_validator import HTTPMethodValidator
from ninja_crud.views.validators.path_validator import PathValidator


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
        update_department = views.UpdateModelView(request_body=DepartmentIn, response_body=DepartmentOut)
    ```

    Note:
        The attribute name (e.g., `update_department`) is flexible and customizable.
        It serves as the name of the route and the operation id in the OpenAPI schema.
    """

    def __init__(
        self,
        payload_schema: Optional[Type[Schema]] = None,
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
            payload_schema (Optional[Type[Schema]], optional): The schema used to deserialize the payload.
                Defaults to None. If not provided, the `default_request_body` of the `ModelViewSet` will be used.
            response_schema (Optional[Type[Schema]], optional): The schema used to serialize the updated instance.
                Defaults to None. If not provided, the `default_response_body` of the `ModelViewSet` will be used.
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
            query_parameters=None,
            request_body=payload_schema,
            response_body=response_schema,
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
        model_class = self.model_viewset_class.model
        payload_schema = self.request_body

        def view(
            request: HttpRequest,
            id: utils.get_id_type(model_class),
            payload: payload_schema,
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

    def _inherit_model_viewset_class_attributes(self) -> None:
        if self.request_body is None:
            self.request_body = self.model_viewset_class.default_request_body
        if self.response_body is None:
            self.response_body = self.model_viewset_class.default_response_body
