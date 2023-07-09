import json
from http import HTTPStatus

from django.http import HttpResponse

from ninja_crud.tests.test_abstract import (
    AbstractModelViewTest,
    ArgOrCallable,
    AuthParams,
    BodyParams,
    PathParams,
    TestCaseType,
)
from ninja_crud.views.create import CreateModelView


class CreateModelViewTest(AbstractModelViewTest):
    model_view = CreateModelView

    def __init__(
        self,
        body_params: ArgOrCallable[BodyParams, TestCaseType],
        path_params: ArgOrCallable[PathParams, TestCaseType] = None,
        auth_params: ArgOrCallable[AuthParams, TestCaseType] = None,
    ) -> None:
        super().__init__(
            path_params=path_params, auth_params=auth_params, body_params=body_params
        )

    def request_create_model(
        self, path_params: dict, auth_params: dict, body_params: dict
    ) -> HttpResponse:
        path = "/" + self.urls_prefix + self.get_model_view().get_path()
        return self.client.post(
            path=path.format(**path_params),
            data=body_params,
            content_type="application/json",
            **auth_params,
        )

    def assert_response_is_created(self, response: HttpResponse):
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
        self.assert_response_is_created(response)

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

    def test_create_model_not_found(self):
        path_params = self.get_path_params()
        if path_params.not_found is None:
            self.test_case.skipTest("No not found path provided")
        response = self.request_create_model(
            path_params=path_params.not_found,
            auth_params=self.get_auth_params().ok,
            body_params=self.get_body_params().ok,
        )
        self.assert_response_is_bad_request(response, status_code=HTTPStatus.NOT_FOUND)
