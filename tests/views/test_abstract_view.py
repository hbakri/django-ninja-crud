import unittest.mock

import django.core.exceptions
import django.test

from ninja_crud import views


class TestAbstractView(django.test.TestCase):
    def test_docstrings(self):
        import http
        from typing import Any, Optional, Tuple, Union

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
                request_body: Optional[ninja.Schema],
            ) -> Union[Any, Tuple[http.HTTPStatus, Any]]:
                return {"message": "Hello, world!"}

        router = ninja.Router()
        view = HelloWorldView()
        view.register_route(router, route_name="hello_world")

        self.assertEqual(
            view.handle_request(
                request=django.http.HttpRequest(),
                path_parameters=None,
                query_parameters=None,
                request_body=None,
            ),
            {"message": "Hello, world!"},
        )

    def test_sanitize_and_merge_router_kwargs(self):
        router_kwargs = {"exclude_unset": True, "other": "value"}
        sanitized_router_kwargs = views.AbstractView._clean_router_kwargs(router_kwargs)

        self.assertDictEqual(sanitized_router_kwargs, router_kwargs)

    def test_sanitize_and_merge_router_kwargs_with_path(self):
        router_kwargs = {"path": "/new_path"}
        with unittest.mock.patch(
            "ninja_crud.views.abstract_view.logger"
        ) as mock_logger:
            sanitized_router_kwargs = views.AbstractView._clean_router_kwargs(
                router_kwargs
            )
            mock_logger.warning.assert_called_once()

        self.assertDictEqual(sanitized_router_kwargs, {})
