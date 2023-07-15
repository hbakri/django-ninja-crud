import json
from http import HTTPStatus
from typing import Callable, List

from django.http import HttpResponse
from django.test import tag

from ninja_crud.tests import QueryParameters
from ninja_crud.tests.test_abstract import (
    AbstractModelViewTest,
    ArgOrCallable,
    AuthHeaders,
    PathParameters,
    TestCaseType,
)
from ninja_crud.views.list import ListModelView


class ListModelViewTest(AbstractModelViewTest):
    model_view = ListModelView

    def __init__(
        self,
        path_parameters: ArgOrCallable[PathParameters, TestCaseType] = None,
        auth_headers: ArgOrCallable[AuthHeaders, TestCaseType] = None,
        query_parameters: ArgOrCallable[QueryParameters, TestCaseType] = None,
    ) -> None:
        super().__init__(
            path_parameters=path_parameters,
            query_parameters=query_parameters,
            auth_headers=auth_headers,
        )

    def request_list_model(
        self, path_parameters: dict, query_parameters: dict, auth_headers: dict
    ) -> HttpResponse:
        path = "/" + self.urls_prefix + self.get_model_view().get_path()
        response = self.client.get(
            path=path.format(**path_parameters),
            data=query_parameters or {},
            content_type="application/json",
            **auth_headers,
        )
        return response

    def assert_response_is_ok(
        self, response: HttpResponse, query_parameters: dict, path_parameters: dict
    ):
        self.test_case.assertEqual(response.status_code, HTTPStatus.OK)
        content = json.loads(response.content)

        model_view: ListModelView = self.get_model_view()
        queryset = model_view.get_queryset(
            self.model_view_set.model,
            path_parameters["id"] if "id" in path_parameters else None,
        )

        limit = query_parameters.pop("limit", 100)
        offset = query_parameters.pop("offset", 0)
        if model_view.filter_schema is not None:
            filter_instance = model_view.filter_schema(**query_parameters)
            queryset = model_view.filter_queryset(queryset, filter_instance)

        self.assert_content_equals_schema_list(
            content,
            queryset=queryset,
            output_schema=model_view.output_schema,
            limit=limit,
            offset=offset,
        )

    def run_sub_tests(
        self,
        path_parameters_list: List[dict],
        query_parameters_list: List[dict],
        auth_headers_list: List[dict],
        completion_callback: Callable[[HttpResponse, dict, dict, dict], None],
    ):
        for path_parameters in path_parameters_list:
            for query_parameters in query_parameters_list:
                for auth_headers in auth_headers_list:
                    with self.test_case.subTest(
                        path_parameters=path_parameters,
                        query_parameters=query_parameters,
                        auth_headers=auth_headers,
                    ):
                        response = self.request_list_model(
                            path_parameters=path_parameters,
                            query_parameters=query_parameters,
                            auth_headers=auth_headers,
                        )
                        completion_callback(
                            response, path_parameters, query_parameters, auth_headers
                        )

    @tag("list")
    def test_list_model_ok(self):
        path_parameters = self.get_path_parameters()
        query_parameters = self.get_query_parameters()
        auth_headers = self.get_auth_headers()
        self.run_sub_tests(
            path_parameters_list=path_parameters.ok,
            query_parameters_list=query_parameters.ok,
            auth_headers_list=auth_headers.ok,
            completion_callback=lambda response, path_parameters_, query_parameters_, _: self.assert_response_is_ok(
                response,
                path_parameters=path_parameters_,
                query_parameters=query_parameters_,
            ),
        )

    @tag("list")
    def test_list_model_bad_request(self):
        path_parameters = self.get_path_parameters()
        query_parameters = self.get_query_parameters()
        auth_headers = self.get_auth_headers()
        if query_parameters.bad_request is None:
            self.test_case.skipTest("No 'bad_request' query parameters provided")
        self.run_sub_tests(
            path_parameters_list=path_parameters.ok,
            query_parameters_list=query_parameters.bad_request,
            auth_headers_list=auth_headers.ok,
            completion_callback=lambda response, _, __, ___: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.BAD_REQUEST
            ),
        )

    @tag("list")
    def test_list_model_unauthorized(self):
        path_parameters = self.get_path_parameters()
        query_parameters = self.get_query_parameters()
        auth_headers = self.get_auth_headers()
        if auth_headers.unauthorized is None:
            self.test_case.skipTest("No 'unauthorized' auth headers provided")
        self.run_sub_tests(
            path_parameters_list=path_parameters.ok,
            query_parameters_list=query_parameters.ok,
            auth_headers_list=auth_headers.unauthorized,
            completion_callback=lambda response, _, __, ___: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.UNAUTHORIZED
            ),
        )

    @tag("list")
    def test_list_model_forbidden(self):
        path_parameters = self.get_path_parameters()
        query_parameters = self.get_query_parameters()
        auth_headers = self.get_auth_headers()
        if auth_headers.forbidden is None:
            self.test_case.skipTest("No 'forbidden' auth headers provided")
        self.run_sub_tests(
            path_parameters_list=path_parameters.ok,
            query_parameters_list=query_parameters.ok,
            auth_headers_list=auth_headers.forbidden,
            completion_callback=lambda response, _, __, ___: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.FORBIDDEN
            ),
        )

    @tag("list")
    def test_list_model_not_found(self):
        path_parameters = self.get_path_parameters()
        query_parameters = self.get_query_parameters()
        auth_headers = self.get_auth_headers()
        if path_parameters.not_found is None:
            self.test_case.skipTest("No 'not_found' path parameters provided")
        self.run_sub_tests(
            path_parameters_list=path_parameters.not_found,
            query_parameters_list=query_parameters.ok,
            auth_headers_list=auth_headers.ok,
            completion_callback=lambda response, _, __, ___: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.NOT_FOUND
            ),
        )
