import json
from http import HTTPStatus
from typing import Callable, List

from django.http import HttpResponse
from django.test import tag

from ninja_crud.tests.test_abstract import (
    AbstractModelViewTest,
    ArgOrCallable,
    AuthHeaders,
    PathParameters,
    Payloads,
    TestCaseType,
)
from ninja_crud.views.create import CreateModelView


class CreateModelViewTest(AbstractModelViewTest):
    model_view = CreateModelView

    def __init__(
        self,
        payloads: ArgOrCallable[Payloads, TestCaseType],
        path_parameters: ArgOrCallable[PathParameters, TestCaseType] = None,
        auth_headers: ArgOrCallable[AuthHeaders, TestCaseType] = None,
    ) -> None:
        super().__init__(
            path_parameters=path_parameters,
            auth_headers=auth_headers,
            payloads=payloads,
        )

    def request_create_model(
        self, path_parameters: dict, auth_headers: dict, payloads: dict
    ) -> HttpResponse:
        path = "/" + self.urls_prefix + self.get_model_view().get_path()
        return self.client.post(
            path=path.format(**path_parameters),
            data=payloads,
            content_type="application/json",
            **auth_headers,
        )

    def assert_response_is_created(self, response: HttpResponse, payloads: dict):
        self.test_case.assertEqual(response.status_code, HTTPStatus.CREATED)
        content = json.loads(response.content)

        model_view: CreateModelView = self.get_model_view()
        if model_view.detail:
            model = model_view.related_model
        else:
            model = self.model_view_set.model
        self.assert_content_equals_schema(
            content,
            queryset=model.objects.get_queryset(),
            output_schema=model_view.output_schema,
        )

    def run_sub_tests(
        self,
        path_parameters_list: List[dict],
        auth_headers_list: List[dict],
        payloads_list: List[dict],
        completion_callback: Callable[[HttpResponse, dict, dict, dict], None],
    ):
        for path_parameters in path_parameters_list:
            for auth_headers in auth_headers_list:
                for payloads in payloads_list:
                    with self.test_case.subTest(
                        path_parameters=path_parameters,
                        auth_headers=auth_headers,
                        payloads=payloads,
                    ):
                        response = self.request_create_model(
                            path_parameters=path_parameters,
                            auth_headers=auth_headers,
                            payloads=payloads,
                        )
                        completion_callback(
                            response, path_parameters, auth_headers, payloads
                        )

    @tag("create")
    def test_create_model_ok(self):
        path_parameters = self.get_path_parameters()
        auth_headers = self.get_auth_headers()
        payloads = self.get_payloads()
        self.run_sub_tests(
            path_parameters_list=path_parameters.ok,
            auth_headers_list=auth_headers.ok,
            payloads_list=payloads.ok,
            completion_callback=lambda response, _, __, payloads_: self.assert_response_is_created(
                response, payloads=payloads_
            ),
        )

    @tag("create")
    def test_create_model_bad_request(self):
        path_parameters = self.get_path_parameters()
        auth_headers = self.get_auth_headers()
        payloads = self.get_payloads()
        if payloads.bad_request is None:
            self.test_case.skipTest("No 'bad_request' payload provided")
        self.run_sub_tests(
            path_parameters_list=path_parameters.ok,
            auth_headers_list=auth_headers.ok,
            payloads_list=payloads.bad_request,
            completion_callback=lambda response, _, __, ___: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.BAD_REQUEST
            ),
        )

    @tag("create")
    def test_create_model_conflict(self):
        path_parameters = self.get_path_parameters()
        auth_headers = self.get_auth_headers()
        payloads = self.get_payloads()
        if payloads.conflict is None:
            self.test_case.skipTest("No 'conflict' payload provided")
        self.run_sub_tests(
            path_parameters_list=path_parameters.ok,
            auth_headers_list=auth_headers.ok,
            payloads_list=payloads.conflict,
            completion_callback=lambda response, _, __, ___: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.CONFLICT
            ),
        )

    @tag("create")
    def test_create_model_unauthorized(self):
        path_parameters = self.get_path_parameters()
        auth_headers = self.get_auth_headers()
        payloads = self.get_payloads()
        if auth_headers.unauthorized is None:
            self.test_case.skipTest("No 'unauthorized' auth headers provided")
        self.run_sub_tests(
            path_parameters_list=path_parameters.ok,
            auth_headers_list=auth_headers.unauthorized,
            payloads_list=payloads.ok,
            completion_callback=lambda response, _, __, ___: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.UNAUTHORIZED
            ),
        )

    @tag("create")
    def test_create_model_forbidden(self):
        path_parameters = self.get_path_parameters()
        auth_headers = self.get_auth_headers()
        payloads = self.get_payloads()
        if auth_headers.forbidden is None:
            self.test_case.skipTest("No 'forbidden' auth headers provided")
        self.run_sub_tests(
            path_parameters_list=path_parameters.ok,
            auth_headers_list=auth_headers.forbidden,
            payloads_list=payloads.ok,
            completion_callback=lambda response, _, __, ___: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.FORBIDDEN
            ),
        )

    @tag("create")
    def test_create_model_not_found(self):
        path_parameters = self.get_path_parameters()
        auth_headers = self.get_auth_headers()
        payloads = self.get_payloads()
        if path_parameters.not_found is None:
            self.test_case.skipTest("No 'not_found' path parameters provided")
        self.run_sub_tests(
            path_parameters_list=path_parameters.not_found,
            auth_headers_list=auth_headers.ok,
            payloads_list=payloads.ok,
            completion_callback=lambda response, _, __, ___: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.NOT_FOUND
            ),
        )
