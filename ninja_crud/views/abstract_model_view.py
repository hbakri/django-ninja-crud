import abc
import http
from typing import TYPE_CHECKING, Callable, List, Optional, Type

from ninja import FilterSchema, Schema

from ninja_crud.views.abstract_view import AbstractView
from ninja_crud.views.enums import HTTPMethod

if TYPE_CHECKING:  # pragma: no cover
    from ninja_crud.viewsets import ModelViewSet


class AbstractModelView(AbstractView, abc.ABC):
    """
    Abstract base class for creating model views for Django Ninja APIs.

    This class provides a template for defining HTTP routes, request handling,
    and response formation. Subclasses should implement the build_view method
    to define specific view logic.
    """

    def __init__(
        self,
        method: HTTPMethod,
        path: str,
        filter_schema: Optional[Type[FilterSchema]] = None,
        payload_schema: Optional[Type[Schema]] = None,
        response_schema: Optional[Type[Schema]] = None,
        response_status: http.HTTPStatus = http.HTTPStatus.OK,
        decorators: Optional[List[Callable]] = None,
        router_kwargs: Optional[dict] = None,
    ) -> None:
        """
        Initializes the AbstractModelView with the given decorators and optional router keyword arguments.

        Args:
            method (HTTPMethod): The HTTP method for the view.
            path (str): The path to use for the view.
            filter_schema (Optional[Type[FilterSchema]], optional): The schema used to deserialize the query parameters.
                Defaults to None.
            payload_schema (Optional[Type[Schema]], optional): The schema used to deserialize the payload.
                Defaults to None.
            response_schema (Optional[Type[Schema]], optional): The schema used to serialize the response body.
                Defaults to None.
            decorators (Optional[List[Callable]], optional): A list of decorators to apply to the view. Defaults to [].
            router_kwargs (Optional[dict], optional): Additional arguments to pass to the router. Defaults to {}.
                Overrides are allowed for most arguments except 'path', 'methods', and 'response'. If any of these
                arguments are provided, a warning will be logged and the override will be ignored.
        """
        super().__init__(
            method=method,
            path=path,
            query_parameters=filter_schema,
            request_body=payload_schema,
            response_body=response_schema,
            response_status=response_status,
            decorators=decorators,
            router_kwargs=router_kwargs,
        )
        self.model_viewset_class: Optional[Type["ModelViewSet"]] = None

    def bind_to_viewset(
        self, viewset_class: Type["ModelViewSet"], model_view_name: str
    ) -> None:
        self.model_viewset_class = viewset_class

    def get_model_viewset_class(self) -> Type["ModelViewSet"]:
        if self.model_viewset_class is None:
            raise ValueError(
                f"Viewset class not bound to {self.__class__.__name__}. "
                "Please call bind_to_viewset() before calling this method."
            )
        return self.model_viewset_class

    def bind_default_value(
        self,
        viewset_class: Type["ModelViewSet"],
        model_view_name: str,
        attribute_name: str,
        default_attribute_name: str,
    ):
        if getattr(self, attribute_name, None) is None:
            default_attribute = getattr(viewset_class, default_attribute_name, None)
            if default_attribute is None:
                raise ValueError(
                    f"Could not determine '{attribute_name}' for {viewset_class.__name__}.{model_view_name}."
                )
            setattr(self, attribute_name, default_attribute)

    def bind_default_payload_schema(
        self, viewset_class: Type["ModelViewSet"], model_view_name: str
    ) -> None:
        self.bind_default_value(
            viewset_class=viewset_class,
            model_view_name=model_view_name,
            attribute_name="request_body",
            default_attribute_name="default_payload_schema",
        )

    def bind_default_response_schema(
        self, viewset_class: Type["ModelViewSet"], model_view_name: str
    ) -> None:
        self.bind_default_value(
            viewset_class=viewset_class,
            model_view_name=model_view_name,
            attribute_name="response_body",
            default_attribute_name="default_response_schema",
        )
