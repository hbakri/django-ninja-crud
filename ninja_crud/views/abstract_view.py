import abc
import functools
import http
import logging
from typing import Callable, Dict, List, Optional, Type, Union

import django.http
import ninja

from ninja_crud.views.enums import HTTPMethod

logger = logging.getLogger(__name__)


class AbstractView(abc.ABC):
    """
    Abstract base class for creating views for Django Ninja APIs.

    This class provides a template for defining HTTP routes, request handling,
    and response formation. Subclasses should implement the build_view method
    to define specific view logic.

    Args:
        method (HTTPMethod): HTTP method for the route.
        path (str): Path for the route.
        query_parameters (Optional[Type[ninja.Schema]], optional): Schema for
            deserializing query parameters. Defaults to None.
        request_body (Optional[Type[ninja.Schema]], optional): Schema for
            deserializing the request body. Defaults to None.
        response_body (Optional[Type[ninja.Schema]], optional): Schema for
            serializing the response body. Defaults to None.
        response_status (http.HTTPStatus, optional): HTTP status code for the
            response. Defaults to http.HTTPStatus.OK.
        decorators (Optional[List[Callable]], optional): Decorators for the view.
            Defaults to [].
        router_kwargs (Optional[Dict], optional): Additional router arguments.
            Defaults to {}. Overrides are ignored for 'path', 'methods', and
            'response'.

    Examples:
    ```python
    # examples/abstract_views.py
    from typing import Type, Callable

    import django.http
    import ninja

    from ninja_crud import views

    class HelloWorldSchema(ninja.Schema):
        message: str

    class HelloWorldView(views.AbstractView):
        def __init__(self) -> None:
            super().__init__(
                method=views.enums.HTTPMethod.GET,
                path="/hello-world/",
                response_body=HelloWorldSchema,
            )

        def build_view(self) -> Callable:
            def view(request: django.http.HttpRequest):
                return {"message": "Hello, world!"}
            return view
    ```
    """

    def __init__(
        self,
        method: HTTPMethod,
        path: str,
        query_parameters: Optional[Type[ninja.Schema]] = None,
        request_body: Optional[Type[ninja.Schema]] = None,
        response_body: Union[Type[ninja.Schema], Type[List[ninja.Schema]], None] = None,
        response_status: http.HTTPStatus = http.HTTPStatus.OK,
        decorators: Optional[List[Callable]] = None,
        router_kwargs: Optional[Dict] = None,
    ) -> None:
        self.method = method
        self.path = path
        self.query_parameters = query_parameters
        self.request_body = request_body
        self.response_body = response_body
        self.response_status = response_status
        self.decorators = decorators or []
        self.router_kwargs = router_kwargs or {}

    @abc.abstractmethod
    def build_view(self) -> Callable:
        """
        Abstract method to build the view function.

        Subclasses should implement this method to define the view logic.

        Returns:
            Callable: The constructed view function.
        """
        pass

    def register_route(self, router: ninja.Router, route_name: str) -> None:
        """
        Registers a view with the specified router under the given route name.

        This method builds the view function using build_view, sets its name to
        the provided route_name, and then registers it with the router. It uses
        the route configuration specified in the constructor (HTTP method, path,
        response structure, etc.) to set up the route.

        Args:
            router (ninja.Router): The router with which to register the view.
            route_name (str): The name of the route. This name is used as the
                function name for the view and as the operation id in the OpenAPI
                schema.

        Example:
        ```python
        import ninja

        from examples.abstract_views import HelloWorldView

        router = ninja.Router()
        view = HelloWorldView()
        view.register_route(router, route_name="hello_world")
        ```
        """
        view = self.build_view()
        view.__name__ = route_name
        self._build_route_decorator(router=router)(view)

    def _build_route_decorator(self, router: ninja.Router) -> Callable:
        def route_decorator(view: Callable):
            for decorator in reversed(self.decorators):
                view = decorator(view)

            @router.api_operation(**self._get_router_kwargs(view.__name__))
            @functools.wraps(view)
            def wrapped_view(request: django.http.HttpRequest, *args, **kwargs):
                return view(request, *args, **kwargs)

            return wrapped_view

        return route_decorator

    def _get_router_kwargs(self, operation_id: str) -> dict:
        return {
            "methods": [self.method.value],
            "path": self.path,
            "response": {self.response_status.value: self.response_body},
            "operation_id": operation_id,
            **self._clean_router_kwargs(self.router_kwargs),
        }

    @staticmethod
    def _clean_router_kwargs(router_kwargs: dict) -> dict:
        locked_keys = ["methods", "path", "response"]
        cleaned_kwargs = router_kwargs.copy()
        for locked_key in locked_keys:
            if locked_key in cleaned_kwargs:
                logger.warning(f"Cannot override '{locked_key}' in 'router_kwargs'.")
                cleaned_kwargs.pop(locked_key)

        return cleaned_kwargs
