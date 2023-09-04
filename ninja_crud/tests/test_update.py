import json
import logging
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
from ninja_crud.tests.test_abstract import AbstractTestModelView
from ninja_crud.views.update import UpdateModelView

logger = logging.getLogger(__name__)


class TestUpdateModelView(AbstractTestModelView):
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
        path = "/" + self.test_model_view_set.base_path + self.model_view.get_path()
        return self.test_model_view_set.client_class().put(
            path=path.format(**path_parameters),
            data=payload,
            content_type="application/json",
            **auth_headers,
        )

    def assert_response_is_ok(self, response: HttpResponse, payload: dict):
        self.test_model_view_set.assertEqual(response.status_code, HTTPStatus.OK)
        content = json.loads(response.content)

        TestAssertionHelper.assert_content_equals_schema(
            test_case=self.test_model_view_set,
            content=content,
            queryset=self.test_model_view_set.model_view_set_class.model_class.objects.get_queryset(),
            schema_class=self.model_view.output_schema,
        )

    def assert_response_is_bad_request(
        self, response: HttpResponse, status_code: HTTPStatus
    ):
        TestAssertionHelper.assert_response_is_bad_request(
            self.test_model_view_set, response, status_code=status_code
        )

    @tag("update")
    def test_update_model_ok(self):
        self.request_composer.test_view_ok(
            test_case=self.test_model_view_set,
            completion_callback=lambda response, _, __, ___, payload: self.assert_response_is_ok(
                response, payload=payload
            ),
        )

    @tag("update")
    def test_update_model_bad_request(self):
        self.request_composer.test_view_payloads_bad_request(
            test_case=self.test_model_view_set,
            completion_callback=lambda response, _, __, ___, ____: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.BAD_REQUEST
            ),
        )

    @tag("update")
    def test_update_model_conflict(self):
        self.request_composer.test_view_payloads_conflict(
            test_case=self.test_model_view_set,
            completion_callback=lambda response, _, __, ___, ____: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.CONFLICT
            ),
        )

    @tag("update")
    def test_update_model_unauthorized(self):
        self.request_composer.test_view_auth_headers_unauthorized(
            test_case=self.test_model_view_set,
            completion_callback=lambda response, _, __, ___, ____: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.UNAUTHORIZED
            ),
        )

    @tag("update")
    def test_update_model_forbidden(self):
        self.request_composer.test_view_auth_headers_forbidden(
            test_case=self.test_model_view_set,
            completion_callback=lambda response, _, __, ___, ____: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.FORBIDDEN
            ),
        )

    @tag("update")
    def test_update_model_not_found(self):
        self.request_composer.test_view_path_parameters_not_found(
            test_case=self.test_model_view_set,
            completion_callback=lambda response, _, __, ___, ____: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.NOT_FOUND
            ),
        )


class UpdateModelViewTest(TestUpdateModelView):
    def __init__(self, *args, **kwargs):  # pragma: no cover
        logger.warning(
            f"{UpdateModelViewTest.__name__} is deprecated, use {TestUpdateModelView.__name__} instead",
            DeprecationWarning,
        )
        super().__init__(*args, **kwargs)
