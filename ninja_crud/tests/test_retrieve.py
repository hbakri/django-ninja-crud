import json
import logging
from http import HTTPStatus
from typing import Optional

from django.http import HttpResponse
from django.test import tag

from ninja_crud.tests.assertion_helper import TestAssertionHelper
from ninja_crud.tests.request_components import AuthHeaders, PathParameters
from ninja_crud.tests.test_abstract import AbstractTestModelView
from ninja_crud.tests.test_composer import ArgOrCallable, TestCaseType, TestComposer
from ninja_crud.views.retrieve import RetrieveModelView

logger = logging.getLogger(__name__)


class TestRetrieveModelView(AbstractTestModelView):
    model_view: RetrieveModelView

    def __init__(
        self,
        path_parameters: ArgOrCallable[PathParameters, TestCaseType],
        auth_headers: Optional[ArgOrCallable[AuthHeaders, TestCaseType]] = None,
    ) -> None:
        super().__init__(model_view_class=RetrieveModelView)
        self.test_composer = TestComposer(
            perform_request=self.perform_request,
            path_parameters=path_parameters,
            auth_headers=auth_headers,
        )

    def perform_request(
        self,
        path_parameters: dict,
        query_parameters: dict,
        auth_headers: dict,
        payload: dict,
    ) -> HttpResponse:
        path = "/" + self.test_model_view_set.base_path + self.model_view.path
        return self.test_model_view_set.client_class().get(
            path=path.format(**path_parameters),
            content_type="application/json",
            **auth_headers,
        )

    def on_successful_request(
        self,
        response: HttpResponse,
        path_parameters: dict,
        query_parameters: dict,
        auth_headers: dict,
        payload: dict,
    ):
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

    def on_failed_request(
        self,
        response: HttpResponse,
        path_parameters: dict,
        query_parameters: dict,
        auth_headers: dict,
        payload: dict,
    ):
        pass

    @tag("retrieve")
    def test_retrieve_model_ok(self):
        self.test_composer.test_view_ok(
            test_case=self.test_model_view_set,
            on_completion=self.on_successful_request,
            status=HTTPStatus.OK,
        )

    @tag("retrieve")
    def test_retrieve_model_unauthorized(self):
        self.test_composer.test_view_auth_headers_unauthorized(
            test_case=self.test_model_view_set,
            on_completion=self.on_failed_request,
        )

    @tag("retrieve")
    def test_retrieve_model_forbidden(self):
        self.test_composer.test_view_auth_headers_forbidden(
            test_case=self.test_model_view_set,
            on_completion=self.on_failed_request,
        )

    @tag("retrieve")
    def test_retrieve_model_not_found(self):
        self.test_composer.test_view_path_parameters_not_found(
            test_case=self.test_model_view_set,
            on_completion=self.on_failed_request,
        )


class RetrieveModelViewTest(TestRetrieveModelView):
    def __init__(self, *args, **kwargs):  # pragma: no cover
        logger.warning(
            f"{RetrieveModelViewTest.__name__} is deprecated, use {TestRetrieveModelView.__name__} instead",
            DeprecationWarning,
        )
        super().__init__(*args, **kwargs)
