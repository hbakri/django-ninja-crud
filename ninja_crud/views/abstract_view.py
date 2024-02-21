import abc
import functools
import http
import logging
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union

import django.http
import ninja

from ninja_crud.views.enums import HTTPMethod

logger = logging.getLogger(__name__)


class AbstractView(abc.ABC):
    """
    An abstract view class that handles common patterns and functionality.

    This class provides a base for creating views that handle HTTP requests and
    responses. It includes methods for defining the view's request handling logic,
    creating the view handler function, registering the view with a router, and
    configuring the view's routing.

    Args:
        method (HTTPMethod): View HTTP method.
        path (str): View path.
        path_parameters (Optional[Type[ninja.Schema]], optional): Schema for
            deserializing path parameters. Defaults to None.
        query_parameters (Optional[Type[ninja.Schema]], optional): Schema for
            deserializing query parameters. Defaults to None.
        request_body (Optional[Type[ninja.Schema]], optional): Schema for deserializing
            the request body. Defaults to None.
        response_body (Optional[Type[ninja.Schema]], optional): Schema for serializing
            the response body. Defaults to None.
        response_status (http.HTTPStatus, optional): HTTP status code for the response.
            Defaults to http.HTTPStatus.OK.
        decorators (Optional[List[Callable]], optional): Decorators for the view.
            Defaults to [].
        router_kwargs (Optional[Dict], optional): Additional router arguments, with
            overrides for 'path', 'methods', and 'response' being ignored. Defaults
            to {}.

    Examples:
    ```python
    # examples/abstract_views.py
    import http
    from typing import Union, Any, Optional, Tuple

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

        def handle_request(
            self,
            request: django.http.HttpRequest,
            path_parameters: Optional[ninja.Schema],
            query_parameters: Optional[ninja.Schema],
            request_body: Optional[ninja.Schema]
        ) -> Union[Any, Tuple[http.HTTPStatus, Any]]:
            return {"message": "Hello, world!"}
    ```

    Note:
        Subclasses should implement the `handle_request` method to define the view's
    """

    def __init__(
        self,
        method: HTTPMethod,
        path: str,
        path_parameters: Optional[Type[ninja.Schema]] = None,
        query_parameters: Optional[Type[ninja.Schema]] = None,
        request_body: Optional[Type[ninja.Schema]] = None,
        response_body: Union[Type[ninja.Schema], Type[List[ninja.Schema]], None] = None,
        response_status: http.HTTPStatus = http.HTTPStatus.OK,
        decorators: Optional[List[Callable]] = None,
        router_kwargs: Optional[Dict] = None,
    ) -> None:
        self.method = method
        self.path = path
        self.path_parameters = path_parameters
        self.query_parameters = query_parameters
        self.request_body = request_body
        self.response_body = response_body
        self.response_status = response_status
        self.decorators = decorators or []
        self.router_kwargs = router_kwargs or {}

    @abc.abstractmethod
    def handle_request(
        self,
        request: django.http.HttpRequest,
        path_parameters: Optional[ninja.Schema],
        query_parameters: Optional[ninja.Schema],
        request_body: Optional[ninja.Schema],
    ) -> Union[Any, Tuple[http.HTTPStatus, Any]]:  # pragma: no cover
        """
        Handles the request and returns the response.

        Subclasses should implement this method to define the view's request
        handling logic. This method should take the request and any deserialized
        parameters and return the response body. If the response status is not
        the default (200 OK), then the method should return a tuple with the
        status and the response body.

        Args:
            request (django.http.HttpRequest): The request object.
            path_parameters (Optional[ninja.Schema]): Deserialized path parameters.
            query_parameters (Optional[ninja.Schema]): Deserialized query parameters.
            request_body (Optional[ninja.Schema]): Deserialized request body.

        Returns:
            Union[Any, Tuple[http.HTTPStatus, Any]]: The response body. If the
                response status is not the default (200 OK), then the method
                should return a tuple with the status and the response body.
        """
        raise NotImplementedError

    def create_view_handler(self) -> Callable:
        path_parameters_schema_class: Optional[
            Type[ninja.Schema]
        ] = self.path_parameters
        query_parameters_schema_class: Optional[
            Type[ninja.Schema]
        ] = self.query_parameters
        request_body_schema_class: Optional[Type[ninja.Schema]] = self.request_body

        def view_handler(
            request: django.http.HttpRequest,
            path_parameters: path_parameters_schema_class = ninja.Path(
                default=None, include_in_schema=False
            ),
            query_parameters: query_parameters_schema_class = ninja.Query(
                default=None, include_in_schema=False
            ),
            request_body: request_body_schema_class = ninja.Body(
                default=None, include_in_schema=False
            ),
        ):
            return self.handle_request(
                request=request,
                path_parameters=path_parameters,
                query_parameters=query_parameters,
                request_body=request_body,
            )

        return view_handler

    def register_route(self, router: ninja.Router, route_name: str) -> None:
        """
        Registers a view with the specified router under the given route name.

        This method builds the view function using create_view_handler, sets its name to
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
        view = self.create_view_handler()
        view.__name__ = route_name
        self.configure_view_routing(router=router)(view)

    def configure_view_routing(self, router: ninja.Router) -> Callable:
        def route_decorator(view: Callable):
            for decorator in reversed(self.decorators):
                view = decorator(view)

            @router.api_operation(**self._get_router_kwargs(view.__name__))
            @functools.wraps(view)
            def wrapped_view(request: django.http.HttpRequest, *args, **kwargs):
                return view(request, *args, **kwargs)

            return wrapped_view

        return route_decorator

    def _get_router_kwargs(self, operation_id: str) -> Dict[str, Any]:
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
