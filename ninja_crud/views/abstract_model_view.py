import functools
import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable, List, Optional, Type

from django.db.models import Model
from django.http import HttpRequest
from ninja import Router

from ninja_crud.views.enums import HTTPMethod
from ninja_crud.views.helpers import utils
from ninja_crud.views.validators.http_method_validator import HTTPMethodValidator

if TYPE_CHECKING:  # pragma: no cover
    from ninja_crud.viewsets import ModelViewSet

logger = logging.getLogger(__name__)


class AbstractModelView(ABC):
    """
    An abstract base class for all model views.

    Subclasses must implement the `build_view` and `get_response` methods.
    """

    def __init__(
        self,
        method: HTTPMethod,
        path: str,
        decorators: Optional[List[Callable]] = None,
        router_kwargs: Optional[dict] = None,
    ) -> None:
        """
        Initializes the AbstractModelView with the given decorators and optional router keyword arguments.

        Args:
            method (HTTPMethod): The HTTP method for the view.
            path (str): The path to use for the view.
            decorators (Optional[List[Callable]], optional): A list of decorators to apply to the view. Defaults to [].
            router_kwargs (Optional[dict], optional): Additional arguments to pass to the router. Defaults to {}.
                Overrides are allowed for most arguments except 'path', 'methods', and 'response'. If any of these
                arguments are provided, a warning will be logged and the override will be ignored.
        """
        HTTPMethodValidator.validate(method=method)
        self.method = method
        self.path = path
        self.decorators = decorators or []
        self.router_kwargs = router_kwargs or {}
        self.viewset_class: Optional[Type["ModelViewSet"]] = None

    @abstractmethod
    def build_view(self, model_class: Type[Model]) -> Callable:  # pragma: no cover
        """
        Builds the view function for the route.

        Args:
            model_class (Type[Model]): The Django model class for which the route should be created.

        Returns:
            Callable: The view function for the route.

        Raises:
            NotImplementedError: This method must be implemented by a subclass.
        """
        pass

    def register_route(
        self, router: Router, view_name: str, model_class: Type[Model]
    ) -> None:
        view = self.build_view(model_class=model_class)
        view.__name__ = view_name
        self._create_route_decorator(router=router)(view)

    def _create_route_decorator(self, router: Router):
        def route_decorator(view: Callable):
            @router.api_operation(**self._get_router_kwargs(view.__name__))
            @utils.merge_decorators(self.decorators)
            @functools.wraps(view)
            def wrapped_view(request: HttpRequest, *args, **kwargs):
                return view(request, *args, **kwargs)

            return wrapped_view

        return route_decorator

    def _get_router_kwargs(self, operation_id: str) -> dict:
        return {
            "methods": [self.method.value],
            "path": self.path,
            "response": self.get_response(),
            "operation_id": operation_id,
            **self._sanitize_router_kwargs(self.router_kwargs),
        }

    @staticmethod
    def _sanitize_router_kwargs(router_kwargs: dict) -> dict:
        locked_keys = ["methods", "path", "response"]
        sanitized_kwargs = router_kwargs.copy()
        for locked_key in locked_keys:
            if locked_key in sanitized_kwargs:
                logger.warning(f"Cannot override '{locked_key}' in 'router_kwargs'.")
                sanitized_kwargs.pop(locked_key)

        return sanitized_kwargs

    @abstractmethod
    def get_response(self) -> dict:  # pragma: no cover
        """
        Provides a mapping of HTTP status codes to response schemas for the view.

        This response schema is used in API documentation to describe the response body for this view.
        The response schema is critical and cannot be overridden using `router_kwargs`. Any overrides
        will be ignored.

        Returns:
            dict: A mapping of HTTP status codes to response schemas for the view.

        Raises:
            NotImplementedError: This method must be implemented by a subclass.
        """
        pass

    def bind_to_viewset(
        self, viewset_class: Type["ModelViewSet"], model_view_name: str
    ) -> None:
        self.viewset_class = viewset_class

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
