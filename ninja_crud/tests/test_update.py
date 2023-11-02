import json
import logging
from http import HTTPStatus
from typing import Optional

from django.http import HttpResponse
from django.test import tag

from ninja_crud.tests.assertion_helper import TestAssertionHelper
from ninja_crud.tests.request_components import AuthHeaders, PathParameters, Payloads
from ninja_crud.tests.test_abstract import AbstractTestModelView
from ninja_crud.tests.test_composer import ArgOrCallable, TestCaseType, TestComposer
from ninja_crud.views.update import UpdateModelView

logger = logging.getLogger(__name__)


class TestUpdateModelView(AbstractTestModelView):
    model_view: UpdateModelView

    def __init__(
        self,
        path_parameters: ArgOrCallable[PathParameters, TestCaseType],
        payloads: ArgOrCallable[Payloads, TestCaseType],
        auth_headers: Optional[ArgOrCallable[AuthHeaders, TestCaseType]] = None,
    ) -> None:
        super().__init__(model_view_class=UpdateModelView)
        self.test_composer = TestComposer(
            perform_request=self.perform_request,
            path_parameters=path_parameters,
            auth_headers=auth_headers,
            payloads=payloads,
        )

    def perform_request(
        self,
        path_parameters: dict,
        query_parameters: dict,
        auth_headers: dict,
        payload: dict,
    ) -> HttpResponse:
        path = "/" + self.test_model_view_set.base_path + self.model_view.path
        return self.test_model_view_set.client_class().generic(
            method=self.model_view.method.value,
            path=path.format(**path_parameters),
            data=json.dumps(payload),
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

        TestAssertionHelper.assert_content_equals_schema(
            test_case=self.test_model_view_set,
            content=content,
            queryset=self.test_model_view_set.model_view_set_class.model_class.objects.get_queryset(),
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

    @tag("update")
    def test_update_model_ok(self):
        self.test_composer.test_view_ok(
            test_case=self.test_model_view_set,
            on_completion=self.on_successful_request,
            status=HTTPStatus.OK,
        )

    @tag("update")
    def test_update_model_bad_request(self):
        self.test_composer.test_view_payloads_bad_request(
            test_case=self.test_model_view_set,
            on_completion=self.on_failed_request,
        )

    @tag("update")
    def test_update_model_conflict(self):
        self.test_composer.test_view_payloads_conflict(
            test_case=self.test_model_view_set,
            on_completion=self.on_failed_request,
        )

    @tag("update")
    def test_update_model_unauthorized(self):
        self.test_composer.test_view_auth_headers_unauthorized(
            test_case=self.test_model_view_set,
            on_completion=self.on_failed_request,
        )

    @tag("update")
    def test_update_model_forbidden(self):
        self.test_composer.test_view_auth_headers_forbidden(
            test_case=self.test_model_view_set,
            on_completion=self.on_failed_request,
        )

    @tag("update")
    def test_update_model_not_found(self):
        self.test_composer.test_view_path_parameters_not_found(
            test_case=self.test_model_view_set,
            on_completion=self.on_failed_request,
        )


class UpdateModelViewTest(TestUpdateModelView):
    def __init__(self, *args, **kwargs):  # pragma: no cover
        logger.warning(
            f"{UpdateModelViewTest.__name__} is deprecated, use {TestUpdateModelView.__name__} instead",
            DeprecationWarning,
        )
        super().__init__(*args, **kwargs)
