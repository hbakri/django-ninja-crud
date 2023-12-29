from http import HTTPStatus
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Type

from django.db.models import Model
from django.http import HttpRequest
from ninja import Schema

from ninja_crud.views.abstract_model_view import AbstractModelView
from ninja_crud.views.enums import HTTPMethod
from ninja_crud.views.helpers import utils
from ninja_crud.views.helpers.types import DetailQuerySetGetter
from ninja_crud.views.validators.path_validator import PathValidator
from ninja_crud.views.validators.queryset_getter_validator import (
    QuerySetGetterValidator,
)

if TYPE_CHECKING:  # pragma: no cover
    from ninja_crud.viewsets import ModelViewSet


class RetrieveModelView(AbstractModelView):
    """
    A view class that handles retrieving a specific instance of a model.
    It allows customization through a queryset getter and also supports decorators.

    Example:
    ```python
    from ninja_crud import views, viewsets

    from examples.models import Department
    from examples.schemas import DepartmentOut

    class DepartmentViewSet(viewsets.ModelViewSet):
        model = Department

        # Usage: Retrieve a department by id
        # GET /{id}
        retrieve_department = views.RetrieveModelView(output_schema=DepartmentOut)
    ```

    Note:
        The attribute name (e.g., `retrieve_department`) is flexible and customizable.
        It serves as the name of the route and the operation id in the OpenAPI schema.
    """

    def __init__(
        self,
        output_schema: Optional[Type[Schema]] = None,
        queryset_getter: Optional[DetailQuerySetGetter] = None,
        path: str = "/{id}",
        decorators: Optional[List[Callable]] = None,
        router_kwargs: Optional[dict] = None,
    ) -> None:
        """
        Initializes the RetrieveModelView.

        Args:
            output_schema (Optional[Type[Schema]], optional): The schema used to serialize the retrieved object.
                Defaults to None. If not provided, the `default_output_schema` of the `ModelViewSet` will be used.
            queryset_getter (Optional[DetailQuerySetGetter], optional): A function to customize the queryset used
                for retrieving the object. Defaults to None. Should have the signature (id: Any) -> QuerySet[Model].

                If not provided, the default manager of the `model` specified in the `ModelViewSet` will be used.
            path (str, optional): The path to use for the view. Defaults to "/{id}". Must include a "{id}" parameter.
            decorators (Optional[List[Callable]], optional): A list of decorators to apply to the view. Defaults to [].
            router_kwargs (Optional[dict], optional): Additional arguments to pass to the router. Defaults to {}.
                Overrides are allowed for most arguments except 'path', 'methods', and 'response'. If any of these
                arguments are provided, a warning will be logged and the override will be ignored.
        """
        super().__init__(
            method=HTTPMethod.GET,
            path=path,
            filter_schema=None,
            input_schema=None,
            output_schema=output_schema,
            decorators=decorators,
            router_kwargs=router_kwargs,
        )

        PathValidator.validate(path=path, allow_no_parameters=False)
        QuerySetGetterValidator.validate(queryset_getter=queryset_getter, path=path)

        self.queryset_getter = queryset_getter

    def build_view(self, model_class: Type[Model]) -> Callable:
        def view(request: HttpRequest, id: utils.get_id_type(model_class)):
            return HTTPStatus.OK, self.retrieve_model(
                request=request, id=id, model_class=model_class
            )

        return view

    def retrieve_model(self, request: HttpRequest, id: Any, model_class: Type[Model]):
        if self.queryset_getter:
            queryset = self.queryset_getter(id)
        else:
            queryset = model_class.objects.get_queryset()

        return queryset.get(pk=id)

    def get_response(self) -> dict:
        """
        Provides a mapping of HTTP status codes to response schemas for the retrieve view.

        This response schema is used in API documentation to describe the response body for this view.
        The response schema is critical and cannot be overridden using `router_kwargs`. Any overrides
        will be ignored.

        Returns:
            dict: A mapping of HTTP status codes to response schemas for the retrieve view.
                Defaults to {200: self.output_schema}. For example, for a model "Department", the response
                schema would be {200: DepartmentOut}.
        """
        return {HTTPStatus.OK: self.output_schema}

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
