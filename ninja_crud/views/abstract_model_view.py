import functools
import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable, List, Optional, Type

from django.db.models import Model
from ninja import Router

from ninja_crud.views.enums import HTTPMethod
from ninja_crud.views.helpers import utils
from ninja_crud.views.validators.path_validator import PathValidator

if TYPE_CHECKING:  # pragma: no cover
    from ninja_crud.viewsets import ModelViewSet

logger = logging.getLogger(__name__)


class AbstractModelView(ABC):
    """
    An abstract base class for all model views.

    Subclasses must implement the `register_route`, `get_response`, `get_operation_id`, and `get_summary` methods.
    """

    def __init__(
        self,
        method: HTTPMethod,
        path: str,
        detail: bool,
        decorators: Optional[List[Callable]] = None,
        router_kwargs: Optional[dict] = None,
    ) -> None:
        """
        Initializes the AbstractModelView with the given decorators and optional router keyword arguments.

        Args:
            method (HTTPMethod): The HTTP method for the view.
            path (str): The path to use for the view.
            detail (bool): Whether the view is for a detail or collection route.
            decorators (Optional[List[Callable]], optional): A list of decorators to apply to the view. Defaults to [].
            router_kwargs (Optional[dict], optional): Additional arguments to pass to the router. Defaults to {}.
                Overrides are allowed for most arguments except 'path', 'methods', and 'response'. If any of these
                arguments are provided, a warning will be logged and the override will be ignored.
        """
        if not isinstance(method, HTTPMethod):
            raise TypeError(
                f"Expected 'method' to be an instance of HTTPMethod, but found type {type(method)}."
            )
        self.method = method
        PathValidator.validate(path, detail)
        self.path = path
        self.detail = detail
        self.decorators = decorators or []
        self.router_kwargs = router_kwargs or {}
        self.viewset_class: Optional[Type["ModelViewSet"]] = None

    @abstractmethod
    def register_route(
        self, router: Router, model_class: Type[Model]
    ) -> None:  # pragma: no cover
        """
        Registers the route with the given router.

        Args:
            router (Router): The router to register the route with.
            model_class (Type[Model]): The Django model class for which the route should be created.

        Raises:
            NotImplementedError: This method must be implemented by a subclass.

        Note:
            This method should be called by the `register_routes` method of the `ModelViewSet` subclass.
            It should not be called directly.
        """
        pass

    def configure_route(self, router: Router, model_class: Type[Model]):
        """
        Configures the route for the given model class with the specified router.

        This method is a key part of the route setup process. It returns a decorator which, when applied to a view
        function in a subclass (like `RetrieveModelView`), automatically handles the necessary configuration for
        routing, including applying any specified decorators and merging router keyword arguments.

        The returned decorator abstracts the intricacies of route configuration, allowing subclasses to focus on the
        specific logic of the view (e.g., retrieval, creation, etc.).

        Args:
            router (Router): The Django Ninja router to register the route with.
            model_class (Type[Model]): The Django model class associated with this route.

        Returns:
            Callable: A decorator for the route function in the subclass, encapsulating the route configuration logic.

        Example:
        In a subclass like `RetrieveModelView`:
        ```python
        def register_route(self, router: Router, model_class: Type[Model]) -> None:
            @self.configure_route(router=router, model_class=model_class)
            def retrieve_model(request: HttpRequest, id: Any):
                # ... view-specific logic ...
        ```

        Note:
            This method should not be called directly by end users. It is used internally in the `register_route`
            method of subclasses.
        """

        def decorator(route_func):
            @router.api_operation(
                **self._sanitize_and_merge_router_kwargs(
                    default_router_kwargs=self._get_default_router_kwargs(model_class),
                    custom_router_kwargs=self.router_kwargs,
                )
            )
            @utils.merge_decorators(self.decorators)
            @functools.wraps(route_func)
            def wrapped_func(*args, **kwargs):
                return route_func(*args, **kwargs)

            return wrapped_func

        return decorator

    @staticmethod
    def _sanitize_and_merge_router_kwargs(
        default_router_kwargs: dict, custom_router_kwargs: dict
    ) -> dict:
        locked_keys = ["methods", "path", "response"]
        router_kwargs = custom_router_kwargs.copy()
        for locked_key in locked_keys:
            if locked_key in router_kwargs:
                logger.warning(f"Cannot override '{locked_key}' in 'router_kwargs'.")
                router_kwargs.pop(locked_key)

        return {**default_router_kwargs, **router_kwargs}

    def _get_default_router_kwargs(self, model_class: Type[Model]) -> dict:
        return {
            "methods": [self.method.value],
            "path": self.path,
            "response": self.get_response(),
            "operation_id": self.get_operation_id(model_class),
            "summary": self.get_summary(model_class),
        }

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

    @abstractmethod
    def get_operation_id(self, model_class: Type[Model]) -> str:  # pragma: no cover
        """
        Provides an operation ID for the view.

        This operation ID is used in API documentation to uniquely identify this view.
        It can be overriden using the `router_kwargs`.

        Args:
            model_class (Type[Model]): The Django model class for which the route should be created.

        Returns:
            str: The operation ID for the view.

        Raises:
            NotImplementedError: This method must be implemented by a subclass.
        """
        pass

    @abstractmethod
    def get_summary(self, model_class: Type[Model]) -> str:  # pragma: no cover
        """
        Provides a summary description for the view.

        This summary is used in API documentation to give a brief description of what this view does.
        It can be overriden using the `router_kwargs`.

        Args:
            model_class (Type[Model]): The Django model class for which the route should be created.

        Returns:
            str: The summary for the view.

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
