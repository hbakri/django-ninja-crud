from http import HTTPStatus
from typing import Any, Callable, List, Optional, Type

from django.db.models import Model, QuerySet
from django.http import HttpRequest
from ninja import Router, Schema

from ninja_crud.views import utils
from ninja_crud.views.abstract import AbstractModelView
from ninja_crud.views.types import DetailQuerySetGetter
from ninja_crud.views.validators.queryset_getter_validator import (
    QuerySetGetterValidator,
)


class RetrieveModelView(AbstractModelView):
    """
    A view class that handles retrieving a specific instance of a model.
    It allows customization through a queryset getter and also supports decorators.

    Example:
        ```python
        from ninja_crud.views import ModelViewSet, RetrieveModelView
        from example.models import Department
        from example.schemas import DepartmentOut

        class DepartmentViewSet(ModelViewSet):
            model_class = Department

            retrieve = RetrieveModelView(output_schema=DepartmentOut)
        ```
    """

    def __init__(
        self,
        output_schema: Type[Schema],
        queryset_getter: DetailQuerySetGetter = None,
        decorators: List[Callable] = None,
        router_kwargs: Optional[dict] = None,
    ) -> None:
        """
        Initializes the RetrieveModelView.

        Args:
            output_schema (Type[Schema]): The schema used to serialize the retrieved object.
            queryset_getter (DetailQuerySetGetter, optional): A function to customize the queryset used
                for retrieving the object. If not provided, the model's default manager is used.
                Should have the signature (id: Any) -> QuerySet[Model].
            decorators (List[Callable], optional): A list of decorators to apply to the view function.
            router_kwargs (Optional[dict], optional): Additional keyword arguments to pass to the Ninja Router.
        """

        super().__init__(decorators=decorators, router_kwargs=router_kwargs)

        QuerySetGetterValidator.validate(queryset_getter, detail=True)

        self.output_schema = output_schema
        self.queryset_getter = queryset_getter

    def register_route(self, router: Router, model_class: Type[Model]) -> None:
        """
        Registers the retrieve route with the given router and model class.

        Args:
            router (Router): The Ninja Router instance to which the route should be added.
            model_class (Type[Model]): The Django model class for which the route should be created.
        """

        @router.get(
            path=self.get_path(),
            response=self.output_schema,
            operation_id=f"retrieve_{utils.to_snake_case(model_class.__name__)}",
            summary=f"Retrieve {model_class.__name__}",
            **self.router_kwargs,
        )
        @utils.merge_decorators(self.decorators)
        def retrieve_model(request: HttpRequest, id: utils.get_id_type(model_class)):
            queryset = self._get_queryset(model_class, id)
            return HTTPStatus.OK, queryset.get(pk=id)

    def _get_queryset(self, model_class: Type[Model], id: Any) -> QuerySet[Model]:
        if self.queryset_getter:
            return self.queryset_getter(id)
        else:
            return model_class.objects.get_queryset()

    def get_path(self) -> str:
        """
        Returns the URL path for this view.

        Returns:
            str: The URL path.
        """
        return "/{id}"
