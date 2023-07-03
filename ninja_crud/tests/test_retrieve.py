import json
from http import HTTPStatus

from django.http import HttpResponse
from django.urls import reverse

from ninja_crud.tests.test_abstract import (
    AbstractModelViewTest,
    ArgOrCallable,
    AuthParams,
    PathParams,
    TestCaseType,
)
from ninja_crud.views.retrieve import RetrieveModelView


class RetrieveModelViewTest(AbstractModelViewTest):
    model_view = RetrieveModelView

    def __init__(
        self,
        path_params: ArgOrCallable[PathParams, TestCaseType],
        auth_params: ArgOrCallable[AuthParams, TestCaseType] = None,
    ) -> None:
        super().__init__(path_params=path_params, auth_params=auth_params)

    def request_retrieve_model(
        self, path_params: dict, auth_params: dict
    ) -> HttpResponse:
        model_view: RetrieveModelView = self.get_model_view()
        url_name = model_view.get_url_name(self.model_view_set.model)
        return self.client.get(
            reverse(f"api:{url_name}", kwargs=path_params),
            content_type="application/json",
            **auth_params,
        )

    def assert_response_is_ok(self, response: HttpResponse, path_params: dict):
        self.test_case.assertEqual(response.status_code, HTTPStatus.OK)
        content = json.loads(response.content)

        model_view: RetrieveModelView = self.get_model_view()
        queryset = model_view.get_queryset(self.model_view_set.model, path_params["id"])
        self.assert_content_equals_schema(
            content,
            queryset=queryset,
            output_schema=model_view.output_schema,
        )

    def test_retrieve_model_ok(self):
        path_params = self.get_path_params()
        response = self.request_retrieve_model(
            path_params=path_params.ok,
            auth_params=self.get_auth_params().ok,
        )
        self.assert_response_is_ok(response, path_params.ok)

    def test_retrieve_model_unauthorized(self):
        auth_params = self.get_auth_params()
        if auth_params.unauthorized is None:
            self.test_case.skipTest("No unauthorized auth provided")
        response = self.request_retrieve_model(
            path_params=self.get_path_params().ok,
            auth_params=auth_params.unauthorized,
        )
        self.assert_response_is_bad_request(
            response, status_code=HTTPStatus.UNAUTHORIZED
        )

    def test_retrieve_model_forbidden(self):
        auth_params = self.get_auth_params()
        if auth_params.forbidden is None:
            self.test_case.skipTest("No forbidden auth provided")
        response = self.request_retrieve_model(
            path_params=self.get_path_params().ok,
            auth_params=auth_params.forbidden,
        )
        self.assert_response_is_bad_request(response, status_code=HTTPStatus.FORBIDDEN)

    def test_retrieve_model_not_found(self):
        path_params = self.get_path_params()
        if path_params.not_found is None:
            self.test_case.skipTest("No not found path provided")
        response = self.request_retrieve_model(
            path_params=path_params.not_found,
            auth_params=self.get_auth_params().ok,
        )
        self.assert_response_is_bad_request(response, status_code=HTTPStatus.NOT_FOUND)
