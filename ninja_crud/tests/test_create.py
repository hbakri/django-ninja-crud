import json
from http import HTTPStatus

from django.http import HttpResponse
from django.urls import reverse

from ninja_crud.tests.test_abstract import (
    AbstractModelViewTest,
    AuthParams,
    BodyParams,
    ParamsOrCallable,
    PathParams,
    TestCaseType,
)
from ninja_crud.views.create import CreateModelView


class CreateModelViewTest(AbstractModelViewTest):
    model_view = CreateModelView

    def __init__(
        self,
        body_params: ParamsOrCallable[BodyParams, TestCaseType],
        path_params: ParamsOrCallable[PathParams, TestCaseType] = None,
        auth_params: ParamsOrCallable[AuthParams, TestCaseType] = None,
    ) -> None:
        if path_params is None:
            path_params = PathParams(ok={})
        super().__init__(path_params=path_params, auth_params=auth_params)
        self.body_params = body_params

    def get_body_params(self) -> BodyParams:
        if callable(self.body_params):
            return self.body_params(self.test_case)
        return self.body_params

    def request_create_model(
        self, path_params: dict, auth_params: dict, body_params: dict
    ) -> HttpResponse:
        model_view: CreateModelView = self.get_model_view()
        url_name = model_view.get_url_name(self.model_view_set.model)
        return self.client.post(
            reverse(f"api:{url_name}", kwargs=path_params),
            data=body_params,
            content_type="application/json",
            **auth_params,
        )

    def assert_response_is_ok(self, response: HttpResponse):
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

    def test_create_model_ok(self):
        response = self.request_create_model(
            path_params=self.get_path_params().ok,
            auth_params=self.get_auth_params().ok,
            body_params=self.get_body_params().ok,
        )
        self.assert_response_is_ok(response)

    def test_create_model_bad_request(self):
        body_params = self.get_body_params()
        if body_params.bad_request is None:
            self.test_case.skipTest("No bad request body provided")
        response = self.request_create_model(
            path_params=self.get_path_params().ok,
            auth_params=self.get_auth_params().ok,
            body_params=body_params.bad_request,
        )
        self.assert_response_is_bad_request(
            response, status_code=HTTPStatus.BAD_REQUEST
        )

    def test_create_model_conflict(self):
        body_params = self.get_body_params()
        if body_params.conflict is None:
            self.test_case.skipTest("No conflict body provided")
        response = self.request_create_model(
            path_params=self.get_path_params().ok,
            auth_params=self.get_auth_params().ok,
            body_params=body_params.conflict,
        )
        self.assert_response_is_bad_request(response, status_code=HTTPStatus.CONFLICT)

    def test_create_model_unauthorized(self):
        auth_params = self.get_auth_params()
        if auth_params.unauthorized is None:
            self.test_case.skipTest("No unauthorized auth provided")
        response = self.request_create_model(
            path_params=self.get_path_params().ok,
            auth_params=auth_params.unauthorized,
            body_params=self.get_body_params().ok,
        )
        self.assert_response_is_bad_request(
            response, status_code=HTTPStatus.UNAUTHORIZED
        )

    def test_create_model_forbidden(self):
        auth_params = self.get_auth_params()
        if auth_params.forbidden is None:
            self.test_case.skipTest("No forbidden auth provided")
        response = self.request_create_model(
            path_params=self.get_path_params().ok,
            auth_params=auth_params.forbidden,
            body_params=self.get_body_params().ok,
        )
        self.assert_response_is_bad_request(response, status_code=HTTPStatus.FORBIDDEN)
