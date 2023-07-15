import json
from http import HTTPStatus
from typing import Callable, List

from django.http import HttpResponse
from django.test import tag

from ninja_crud.tests.request_components import AuthHeaders, PathParameters
from ninja_crud.tests.test_abstract import (
    AbstractModelViewTest,
    ArgOrCallable,
    TestCaseType,
)
from ninja_crud.views.retrieve import RetrieveModelView


class RetrieveModelViewTest(AbstractModelViewTest):
    model_view = RetrieveModelView

    def __init__(
        self,
        path_parameters: ArgOrCallable[PathParameters, TestCaseType],
        auth_headers: ArgOrCallable[AuthHeaders, TestCaseType] = None,
    ) -> None:
        super().__init__(path_parameters=path_parameters, auth_headers=auth_headers)

    def request_retrieve_model(
        self, path_parameters: dict, auth_headers: dict
    ) -> HttpResponse:
        path = "/" + self.urls_prefix + self.get_model_view().get_path()
        return self.client.get(
            path=path.format(**path_parameters),
            content_type="application/json",
            **auth_headers,
        )

    def assert_response_is_ok(self, response: HttpResponse, path_parameters: dict):
        self.test_case.assertEqual(response.status_code, HTTPStatus.OK)
        content = json.loads(response.content)

        model_view: RetrieveModelView = self.get_model_view()
        queryset = model_view.get_queryset(
            self.model_view_set.model, path_parameters["id"]
        )
        self.assert_content_equals_schema(
            content,
            queryset=queryset,
            output_schema=model_view.output_schema,
        )

    def run_sub_tests(
        self,
        path_parameters_list: List[dict],
        auth_headers_list: List[dict],
        completion_callback: Callable[[HttpResponse, dict, dict], None],
    ):
        for path_parameters in path_parameters_list:
            for auth_headers in auth_headers_list:
                with self.test_case.subTest(
                    path_parameters=path_parameters, auth_headers=auth_headers
                ):
                    response = self.request_retrieve_model(
                        path_parameters=path_parameters, auth_headers=auth_headers
                    )
                    completion_callback(response, path_parameters, auth_headers)

    @tag("retrieve")
    def test_retrieve_model_ok(self):
        path_parameters = self.get_path_parameters()
        auth_headers = self.get_auth_headers()
        self.run_sub_tests(
            path_parameters_list=path_parameters.ok,
            auth_headers_list=auth_headers.ok,
            completion_callback=lambda response, path_parameters_, _: self.assert_response_is_ok(
                response, path_parameters=path_parameters_
            ),
        )

    @tag("retrieve")
    def test_retrieve_model_unauthorized(self):
        path_parameters = self.get_path_parameters()
        auth_headers = self.get_auth_headers()
        if auth_headers.unauthorized is None:
            self.test_case.skipTest("No 'unauthorized' auth headers provided")
        self.run_sub_tests(
            path_parameters_list=path_parameters.ok,
            auth_headers_list=auth_headers.unauthorized,
            completion_callback=lambda response, _, __: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.UNAUTHORIZED
            ),
        )

    @tag("retrieve")
    def test_retrieve_model_forbidden(self):
        path_parameters = self.get_path_parameters()
        auth_headers = self.get_auth_headers()
        if auth_headers.forbidden is None:
            self.test_case.skipTest("No 'forbidden' auth headers provided")
        self.run_sub_tests(
            path_parameters_list=path_parameters.ok,
            auth_headers_list=auth_headers.forbidden,
            completion_callback=lambda response, _, __: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.FORBIDDEN
            ),
        )

    @tag("retrieve")
    def test_retrieve_model_not_found(self):
        path_parameters = self.get_path_parameters()
        auth_headers = self.get_auth_headers()
        if path_parameters.not_found is None:
            self.test_case.skipTest("No 'not_found' path parameters provided")
        self.run_sub_tests(
            path_parameters_list=path_parameters.not_found,
            auth_headers_list=auth_headers.ok,
            completion_callback=lambda response, _, __: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.NOT_FOUND
            ),
        )
