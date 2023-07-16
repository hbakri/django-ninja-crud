import json
from http import HTTPStatus

from django.http import HttpResponse
from django.test import tag

from ninja_crud.tests.request_components import AuthHeaders, PathParameters
from ninja_crud.tests.request_composer import RequestComposer
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
        self.request_composer = RequestComposer(
            request_method=self.request_retrieve_model,
            path_parameters=path_parameters,
            auth_headers=auth_headers,
        )

    def request_retrieve_model(
        self,
        path_parameters: dict,
        query_parameters: dict,
        auth_headers: dict,
        payload: dict,
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

    @tag("retrieve")
    def test_retrieve_model_ok(self):
        self.request_composer.test_view_ok(
            test_case=self.test_case,
            completion_callback=lambda response, path_parameters_, _, __, ___: self.assert_response_is_ok(
                response, path_parameters=path_parameters_
            ),
        )

    @tag("retrieve")
    def test_retrieve_model_unauthorized(self):
        self.request_composer.test_view_unauthorized(
            test_case=self.test_case,
            completion_callback=lambda response, _, __, ___, ____: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.UNAUTHORIZED
            ),
        )

    @tag("retrieve")
    def test_retrieve_model_forbidden(self):
        self.request_composer.test_view_forbidden(
            test_case=self.test_case,
            completion_callback=lambda response, _, __, ___, ____: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.FORBIDDEN
            ),
        )

    @tag("retrieve")
    def test_retrieve_model_not_found(self):
        self.request_composer.test_view_not_found(
            test_case=self.test_case,
            completion_callback=lambda response, _, __, ___, ____: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.NOT_FOUND
            ),
        )
