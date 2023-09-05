import json
import logging
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
from ninja_crud.tests.test_abstract import AbstractTestModelView
from ninja_crud.views.retrieve import RetrieveModelView

logger = logging.getLogger(__name__)


class TestRetrieveModelView(AbstractTestModelView):
    model_view_class = RetrieveModelView
    model_view: RetrieveModelView

    def __init__(
        self,
        path_parameters: ArgOrCallable[PathParameters, TestCaseType],
        auth_headers: ArgOrCallable[AuthHeaders, TestCaseType] = None,
    ) -> None:
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
        path = "/" + self.test_model_view_set.base_path + self.model_view.get_path()
        return self.test_model_view_set.client_class().get(
            path=path.format(**path_parameters),
            content_type="application/json",
            **auth_headers,
        )

    def assert_response_is_ok(self, response: HttpResponse, path_parameters: dict):
        self.test_model_view_set.assertEqual(response.status_code, HTTPStatus.OK)
        content = json.loads(response.content)

        queryset = self.model_view._get_queryset(
            self.test_model_view_set.model_view_set_class.model_class,
            path_parameters["id"],
        )
        TestAssertionHelper.assert_content_equals_schema(
            test_case=self.test_model_view_set,
            content=content,
            queryset=queryset,
            schema_class=self.model_view.output_schema,
        )

    def assert_response_is_bad_request(
        self, response: HttpResponse, status_code: HTTPStatus
    ):
        TestAssertionHelper.assert_response_is_bad_request(
            self.test_model_view_set, response, status_code=status_code
        )

    @tag("retrieve")
    def test_retrieve_model_ok(self):
        self.request_composer.test_view_ok(
            test_case=self.test_model_view_set,
            completion_callback=lambda response, path_parameters, _, __, ___: self.assert_response_is_ok(
                response, path_parameters=path_parameters
            ),
        )

    @tag("retrieve")
    def test_retrieve_model_unauthorized(self):
        self.request_composer.test_view_auth_headers_unauthorized(
            test_case=self.test_model_view_set,
            completion_callback=lambda response, _, __, ___, ____: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.UNAUTHORIZED
            ),
        )

    @tag("retrieve")
    def test_retrieve_model_forbidden(self):
        self.request_composer.test_view_auth_headers_forbidden(
            test_case=self.test_model_view_set,
            completion_callback=lambda response, _, __, ___, ____: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.FORBIDDEN
            ),
        )

    @tag("retrieve")
    def test_retrieve_model_not_found(self):
        self.request_composer.test_view_path_parameters_not_found(
            test_case=self.test_model_view_set,
            completion_callback=lambda response, _, __, ___, ____: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.NOT_FOUND
            ),
        )


class RetrieveModelViewTest(TestRetrieveModelView):
    def __init__(self, *args, **kwargs):  # pragma: no cover
        logger.warning(
            f"{RetrieveModelViewTest.__name__} is deprecated, use {TestRetrieveModelView.__name__} instead",
            DeprecationWarning,
        )
        super().__init__(*args, **kwargs)
