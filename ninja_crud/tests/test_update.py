import json
from http import HTTPStatus

from django.http import HttpResponse
from django.test import tag

from ninja_crud.tests.request_components import AuthHeaders, PathParameters, Payloads
from ninja_crud.tests.request_composer import RequestComposer
from ninja_crud.tests.test_abstract import (
    AbstractModelViewTest,
    ArgOrCallable,
    TestCaseType,
)
from ninja_crud.views.update import UpdateModelView


class UpdateModelViewTest(AbstractModelViewTest):
    model_view = UpdateModelView

    def __init__(
        self,
        path_parameters: ArgOrCallable[PathParameters, TestCaseType],
        payloads: ArgOrCallable[Payloads, TestCaseType],
        auth_headers: ArgOrCallable[AuthHeaders, TestCaseType] = None,
    ) -> None:
        super().__init__(
            path_parameters=path_parameters,
            auth_headers=auth_headers,
            payloads=payloads,
        )
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
        path = "/" + self.urls_prefix + self.get_model_view().get_path()
        return self.client.put(
            path=path.format(**path_parameters),
            data=payload,
            content_type="application/json",
            **auth_headers,
        )

    def assert_response_is_ok(self, response: HttpResponse, payload: dict):
        self.test_case.assertEqual(response.status_code, HTTPStatus.OK)
        content = json.loads(response.content)

        model_view: UpdateModelView = self.get_model_view()
        self.assert_content_equals_schema(
            content,
            queryset=self.model_view_set.model.objects.get_queryset(),
            output_schema=model_view.output_schema,
        )

    @tag("update")
    def test_update_model_ok(self):
        self.request_composer.test_view_ok(
            test_case=self.test_case,
            completion_callback=lambda response, _, __, ___, payload_: self.assert_response_is_ok(
                response, payload=payload_
            ),
        )

    @tag("update")
    def test_update_model_bad_request(self):
        self.request_composer.test_view_bad_request(
            test_case=self.test_case,
            completion_callback=lambda response, _, __, ___, ____: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.BAD_REQUEST
            ),
        )

    @tag("update")
    def test_update_model_conflict(self):
        self.request_composer.test_view_conflict(
            test_case=self.test_case,
            completion_callback=lambda response, _, __, ___, ____: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.CONFLICT
            ),
        )

    @tag("update")
    def test_update_model_unauthorized(self):
        self.request_composer.test_view_unauthorized(
            test_case=self.test_case,
            completion_callback=lambda response, _, __, ___, ____: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.UNAUTHORIZED
            ),
        )

    @tag("update")
    def test_update_model_forbidden(self):
        self.request_composer.test_view_forbidden(
            test_case=self.test_case,
            completion_callback=lambda response, _, __, ___, ____: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.FORBIDDEN
            ),
        )

    @tag("update")
    def test_update_model_not_found(self):
        self.request_composer.test_view_not_found(
            test_case=self.test_case,
            completion_callback=lambda response, _, __, ___, ____: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.NOT_FOUND
            ),
        )
