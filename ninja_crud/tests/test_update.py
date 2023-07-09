import json
from http import HTTPStatus

from django.http import HttpResponse

from ninja_crud.tests import PathParams
from ninja_crud.tests.test_abstract import (
    AbstractModelViewTest,
    ArgOrCallable,
    AuthParams,
    BodyParams,
    TestCaseType,
)
from ninja_crud.views.update import UpdateModelView


class UpdateModelViewTest(AbstractModelViewTest):
    model_view = UpdateModelView

    def __init__(
        self,
        body_params: ArgOrCallable[BodyParams, TestCaseType],
        path_params: ArgOrCallable[PathParams, TestCaseType],
        auth_params: ArgOrCallable[AuthParams, TestCaseType] = None,
    ) -> None:
        super().__init__(
            path_params=path_params, auth_params=auth_params, body_params=body_params
        )

    def request_update_model(
        self, path_params: dict, auth_params: dict, body_params: dict
    ) -> HttpResponse:
        path = "/" + self.urls_prefix + self.get_model_view().get_path()
        return self.client.put(
            path=path.format(**path_params),
            data=body_params,
            content_type="application/json",
            **auth_params,
        )

    def assert_response_is_ok(self, response: HttpResponse, body_params: dict):
        self.test_case.assertEqual(response.status_code, HTTPStatus.OK)
        content = json.loads(response.content)

        model_view: UpdateModelView = self.get_model_view()
        self.assert_content_equals_schema(
            content,
            queryset=self.model_view_set.model.objects.get_queryset(),
            output_schema=model_view.output_schema,
        )

    def test_update_model_ok(self):
        body_params = self.get_body_params()
        response = self.request_update_model(
            path_params=self.get_path_params().ok,
            auth_params=self.get_auth_params().ok,
            body_params=body_params.ok,
        )
        self.assert_response_is_ok(response, body_params.ok)

    def test_update_model_bad_request(self):
        body_params = self.get_body_params()
        if body_params.bad_request is None:
            self.test_case.skipTest("No bad request body provided")
        response = self.request_update_model(
            path_params=self.get_path_params().ok,
            auth_params=self.get_auth_params().ok,
            body_params=body_params.bad_request,
        )
        self.assert_response_is_bad_request(
            response, status_code=HTTPStatus.BAD_REQUEST
        )

    def test_update_model_conflict(self):
        body_params = self.get_body_params()
        if body_params.conflict is None:
            self.test_case.skipTest("No conflict body provided")
        response = self.request_update_model(
            path_params=self.get_path_params().ok,
            auth_params=self.get_auth_params().ok,
            body_params=body_params.conflict,
        )
        self.assert_response_is_bad_request(response, status_code=HTTPStatus.CONFLICT)

    def test_update_model_unauthorized(self):
        auth_params = self.get_auth_params()
        if auth_params.unauthorized is None:
            self.test_case.skipTest("No unauthorized auth provided")
        response = self.request_update_model(
            path_params=self.get_path_params().ok,
            auth_params=auth_params.unauthorized,
            body_params=self.get_body_params().ok,
        )
        self.assert_response_is_bad_request(
            response, status_code=HTTPStatus.UNAUTHORIZED
        )

    def test_update_model_forbidden(self):
        auth_params = self.get_auth_params()
        if auth_params.forbidden is None:
            self.test_case.skipTest("No forbidden auth provided")
        response = self.request_update_model(
            path_params=self.get_path_params().ok,
            auth_params=auth_params.forbidden,
            body_params=self.get_body_params().ok,
        )
        self.assert_response_is_bad_request(response, status_code=HTTPStatus.FORBIDDEN)

    def test_update_model_not_found(self):
        path_params = self.get_path_params()
        if path_params.not_found is None:
            self.test_case.skipTest("No not found path provided")
        response = self.request_update_model(
            path_params=path_params.not_found,
            auth_params=self.get_auth_params().ok,
            body_params=self.get_body_params().ok,
        )
        self.assert_response_is_bad_request(response, status_code=HTTPStatus.NOT_FOUND)
