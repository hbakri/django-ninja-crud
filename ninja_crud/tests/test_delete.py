from http import HTTPStatus

from django.http import HttpResponse
from django.test import tag

from ninja_crud.tests.assertion_helper import TestAssertionHelper
from ninja_crud.tests.request_components import AuthHeaders, PathParameters
from ninja_crud.tests.request_composer import (
    ArgOrCallable,
    RequestComposer,
    TestCaseType,
)
from ninja_crud.tests.test_abstract import AbstractModelViewTest
from ninja_crud.views.delete import DeleteModelView


class DeleteModelViewTest(AbstractModelViewTest):
    model_view_class = DeleteModelView

    def __init__(
        self,
        path_parameters: ArgOrCallable[PathParameters, TestCaseType],
        auth_headers: ArgOrCallable[AuthHeaders, TestCaseType] = None,
    ) -> None:
        self.request_composer = RequestComposer(
            request_method=self.request_delete_model,
            path_parameters=path_parameters,
            auth_headers=auth_headers,
        )

    def request_delete_model(
        self,
        path_parameters: dict,
        query_parameters: dict,
        auth_headers: dict,
        payload: dict,
    ) -> HttpResponse:
        path = "/" + self.urls_prefix + self.get_model_view().get_path()
        return self.client.delete(
            path=path.format(**path_parameters),
            content_type="application/json",
            **auth_headers,
        )

    def assert_response_is_no_content(
        self, response: HttpResponse, path_parameters: dict
    ):
        self.test_case.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
        self.test_case.assertEqual(response.content, b"")

        queryset = self.model_view_set.model.objects.filter(id=path_parameters["id"])
        self.test_case.assertEqual(queryset.count(), 0)

    def assert_response_is_bad_request(
        self, response: HttpResponse, status_code: HTTPStatus
    ):
        TestAssertionHelper.assert_response_is_bad_request(
            self.test_case, response, status_code=status_code
        )

    @tag("delete")
    def test_delete_model_ok(self):
        self.request_composer.test_view_ok(
            test_case=self.test_case,
            completion_callback=lambda response, path_parameters, _, __, ___: self.assert_response_is_no_content(
                response, path_parameters=path_parameters
            ),
        )

    @tag("delete")
    def test_delete_model_unauthorized(self):
        self.request_composer.test_view_auth_headers_unauthorized(
            test_case=self.test_case,
            completion_callback=lambda response, _, __, ___, ____: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.UNAUTHORIZED
            ),
        )

    @tag("delete")
    def test_delete_model_forbidden(self):
        self.request_composer.test_view_auth_headers_forbidden(
            test_case=self.test_case,
            completion_callback=lambda response, _, __, ___, ____: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.FORBIDDEN
            ),
        )

    @tag("delete")
    def test_delete_model_not_found(self):
        self.request_composer.test_view_path_parameters_not_found(
            test_case=self.test_case,
            completion_callback=lambda response, _, __, ___, ____: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.NOT_FOUND
            ),
        )
