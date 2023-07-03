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
from ninja_crud.views.delete import DeleteModelView


class DeleteModelViewTest(AbstractModelViewTest):
    model_view = DeleteModelView

    def __init__(
        self,
        path_params: ArgOrCallable[PathParams, TestCaseType],
        auth_params: ArgOrCallable[AuthParams, TestCaseType] = None,
    ) -> None:
        super().__init__(path_params=path_params, auth_params=auth_params)

    def request_delete_model(
        self, path_params: dict, auth_params: dict
    ) -> HttpResponse:
        model_view: DeleteModelView = self.get_model_view()
        url_name = model_view.get_url_name(self.model_view_set.model)
        return self.client.delete(
            reverse(f"api:{url_name}", kwargs=path_params),
            content_type="application/json",
            **auth_params,
        )

    def assert_response_is_no_content(self, response: HttpResponse):
        self.test_case.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
        self.test_case.assertEqual(response.content, b"")

    def test_delete_model_ok(self):
        response = self.request_delete_model(
            path_params=self.get_path_params().ok,
            auth_params=self.get_auth_params().ok,
        )
        self.assert_response_is_no_content(response)

    def test_delete_model_unauthorized(self):
        auth_params = self.get_auth_params()
        if auth_params.unauthorized is None:
            self.test_case.skipTest("No unauthorized auth provided")
        response = self.request_delete_model(
            path_params=self.get_path_params().ok,
            auth_params=auth_params.unauthorized,
        )
        self.assert_response_is_bad_request(
            response, status_code=HTTPStatus.UNAUTHORIZED
        )

    def test_delete_model_forbidden(self):
        auth_params = self.get_auth_params()
        if auth_params.forbidden is None:
            self.test_case.skipTest("No forbidden auth provided")
        response = self.request_delete_model(
            path_params=self.get_path_params().ok,
            auth_params=auth_params.forbidden,
        )
        self.assert_response_is_bad_request(response, status_code=HTTPStatus.FORBIDDEN)

    def test_delete_model_not_found(self):
        path_params = self.get_path_params()
        if path_params.not_found is None:
            self.test_case.skipTest("No not found path provided")
        response = self.request_delete_model(
            path_params=path_params.not_found,
            auth_params=self.get_auth_params().ok,
        )
        self.assert_response_is_bad_request(response, status_code=HTTPStatus.NOT_FOUND)
