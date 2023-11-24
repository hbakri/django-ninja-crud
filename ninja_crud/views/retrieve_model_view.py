from http import HTTPStatus
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Type

from django.db.models import Model
from django.http import HttpRequest
from ninja import Router, Schema

from ninja_crud.views.abstract_model_view import AbstractModelView
from ninja_crud.views.enums import HTTPMethod
from ninja_crud.views.helpers import utils
from ninja_crud.views.helpers.types import DetailQuerySetGetter
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
        # GET /departments/{id}/
        retrieve_department_view = views.RetrieveModelView(output_schema=DepartmentOut)
    ```
    """

    def __init__(
        self,
        output_schema: Optional[Type[Schema]] = None,
        queryset_getter: Optional[DetailQuerySetGetter] = None,
        path: Optional[str] = None,
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
            path (Optional[str], optional): The path to use for the view. Defaults to "/{id}".
            decorators (Optional[List[Callable]], optional): A list of decorators to apply to the view. Defaults to [].
            router_kwargs (Optional[dict], optional): Additional arguments to pass to the router. Defaults to {}.
        """
        if path is None:
            path = self._get_default_path()
        super().__init__(
            method=HTTPMethod.GET,
            path=path,
            detail=True,
            decorators=decorators,
            router_kwargs=router_kwargs,
        )

        QuerySetGetterValidator.validate(queryset_getter, detail=self.detail)

        self.output_schema = output_schema
        self.queryset_getter = queryset_getter

    def register_route(self, router: Router, model_class: Type[Model]) -> None:
        @self.configure_route(router=router, model_class=model_class)
        def retrieve_model(request: HttpRequest, id: utils.get_id_type(model_class)):
            return HTTPStatus.OK, self.retrieve_model(id=id, model_class=model_class)

    def retrieve_model(self, id: Any, model_class: Type[Model]):
        if self.queryset_getter:
            queryset = self.queryset_getter(id)
        else:
            queryset = model_class.objects.get_queryset()

        return queryset.get(pk=id)

    @staticmethod
    def _get_default_path() -> str:
        return "/{id}"

    def get_response(self) -> dict:
        return {HTTPStatus.OK: self.output_schema}

    def get_operation_id(self, model_class: Type[Model]) -> str:
        return f"retrieve_{utils.to_snake_case(model_class.__name__)}"

    def get_summary(self, model_class: Type[Model]) -> str:
        return f"Retrieve {model_class.__name__}"

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
