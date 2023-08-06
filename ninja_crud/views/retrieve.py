from http import HTTPStatus
from typing import Any, Callable, List, Optional, Type

from django.db.models import Model, QuerySet
from django.http import HttpRequest
from ninja import Router, Schema

from ninja_crud.views import utils
from ninja_crud.views.abstract import AbstractModelView

QuerysetGetter = Callable[[Any], QuerySet[Model]]


class RetrieveModelView(AbstractModelView):
    """
    A view class that handles retrieving a specific instance of a model.

    Attributes:
        output_schema (Type[Schema]): The schema used to serialize the retrieved instance.
        queryset_getter (QuerysetGetter, optional): A function that takes an object ID and returns a QuerySet
            for retrieving the object. Defaults to None, in which case the model's default manager is used.
            Should be a function with the signature (id: Any) -> QuerySet[Model].
        decorators (List[Callable], optional): A list of decorators to apply to the view function.
        router_kwargs (Optional[dict], optional): A dictionary of keyword arguments to pass to the router.
    """

    def __init__(
        self,
        output_schema: Type[Schema],
        queryset_getter: QuerysetGetter = None,
        decorators: List[Callable] = None,
        router_kwargs: Optional[dict] = None,
    ) -> None:
        """
        Initializes the RetrieveModelView with the given output schema and optional queryset getter and decorators.

        Args:
            output_schema (Type[Schema]): The schema used to serialize the retrieved object.
            queryset_getter (QuerysetGetter, optional): A function that takes an object ID and returns a QuerySet
                for retrieving the object. Defaults to None, in which case the model's default manager is used.
                Should be a function with the signature (id: Any) -> QuerySet[Model].
            decorators (List[Callable], optional): A list of decorators to apply to the view function.
            router_kwargs (Optional[dict], optional): A dictionary of keyword arguments to pass to the router.
        """

        super().__init__(decorators=decorators, router_kwargs=router_kwargs)
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
            queryset = self.get_queryset(model_class, id)
            instance = queryset.get(pk=id)
            return HTTPStatus.OK, instance

    def get_queryset(self, model_class: Type[Model], id: Any) -> QuerySet[Model]:
        """
        Gets the QuerySet for retrieving the object.

        Args:
            model_class (Type[Model]): The Django model class for which the QuerySet should be obtained.
            id (Any): An object ID to use with the queryset_getter.

        Returns:
            QuerySet[Model]: A QuerySet for retrieving the object.
        """

        if self.queryset_getter is None:
            return model_class.objects.get_queryset()
        else:
            return self.queryset_getter(id)

    def get_path(self) -> str:
        """
        Returns the URL path for this view, used in routing.

        Returns:
            str: The URL path.
        """
        return "/{id}"
