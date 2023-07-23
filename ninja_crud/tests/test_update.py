import json
from http import HTTPStatus

from django.http import HttpResponse
from django.test import tag

from ninja_crud.tests.assertion_helper import TestAssertionHelper
from ninja_crud.tests.request_components import AuthHeaders, PathParameters, Payloads
from ninja_crud.tests.request_composer import (
    ArgOrCallable,
    RequestComposer,
    TestCaseType,
)
from ninja_crud.tests.test_abstract import AbstractModelViewTest
from ninja_crud.views.update import UpdateModelView


class UpdateModelViewTest(AbstractModelViewTest):
    model_view_class = UpdateModelView
    model_view: UpdateModelView

    def __init__(
        self,
        path_parameters: ArgOrCallable[PathParameters, TestCaseType],
        payloads: ArgOrCallable[Payloads, TestCaseType],
        auth_headers: ArgOrCallable[AuthHeaders, TestCaseType] = None,
    ) -> None:
        self.request_composer = RequestComposer(
            request_method=self.request_update_model,
            path_parameters=path_parameters,
            auth_headers=auth_headers,
            payloads=payloads,
        )

    def request_update_model(
        self,
        path_parameters: dict,
        query_parameters: dict,
        auth_headers: dict,
        payload: dict,
    ) -> HttpResponse:
        path = "/" + self.model_view_set_test.urls_prefix + self.model_view.get_path()
        return self.model_view_set_test.client_class().put(
            path=path.format(**path_parameters),
            data=payload,
            content_type="application/json",
            **auth_headers,
        )

    def assert_response_is_ok(self, response: HttpResponse, payload: dict):
        self.model_view_set_test.assertEqual(response.status_code, HTTPStatus.OK)
        content = json.loads(response.content)

        TestAssertionHelper.assert_content_equals_schema(
            test_case=self.model_view_set_test,
            content=content,
            queryset=self.model_view_set_test.model_view_set_class.model_class.objects.get_queryset(),
            output_schema=self.model_view.output_schema,
        )

    def assert_response_is_bad_request(
        self, response: HttpResponse, status_code: HTTPStatus
    ):
        TestAssertionHelper.assert_response_is_bad_request(
            self.model_view_set_test, response, status_code=status_code
        )

    @tag("update")
    def test_update_model_ok(self):
        self.request_composer.test_view_ok(
            test_case=self.model_view_set_test,
            completion_callback=lambda response, _, __, ___, payload: self.assert_response_is_ok(
                response, payload=payload
            ),
        )

    @tag("update")
    def test_update_model_bad_request(self):
        self.request_composer.test_view_payloads_bad_request(
            test_case=self.model_view_set_test,
            completion_callback=lambda response, _, __, ___, ____: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.BAD_REQUEST
            ),
        )

    @tag("update")
    def test_update_model_conflict(self):
        self.request_composer.test_view_payloads_conflict(
            test_case=self.model_view_set_test,
            completion_callback=lambda response, _, __, ___, ____: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.CONFLICT
            ),
        )

    @tag("update")
    def test_update_model_unauthorized(self):
        self.request_composer.test_view_auth_headers_unauthorized(
            test_case=self.model_view_set_test,
            completion_callback=lambda response, _, __, ___, ____: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.UNAUTHORIZED
            ),
        )

    @tag("update")
    def test_update_model_forbidden(self):
        self.request_composer.test_view_auth_headers_forbidden(
            test_case=self.model_view_set_test,
            completion_callback=lambda response, _, __, ___, ____: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.FORBIDDEN
            ),
        )

    @tag("update")
    def test_update_model_not_found(self):
        self.request_composer.test_view_path_parameters_not_found(
            test_case=self.model_view_set_test,
            completion_callback=lambda response, _, __, ___, ____: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.NOT_FOUND
            ),
        )
