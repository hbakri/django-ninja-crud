import json
from http import HTTPStatus
from typing import Optional

from django.http import HttpResponse
from django.test import tag

from ninja_crud.testing.core import ArgOrCallable, TestCaseType, ViewTestManager
from ninja_crud.testing.core.components import Headers, PathParameters, Payloads
from ninja_crud.testing.views import AbstractModelViewTest
from ninja_crud.testing.views.helpers import TestAssertionHelper
from ninja_crud.views.update_model_view import UpdateModelView


class UpdateModelViewTest(AbstractModelViewTest):
    model_view: UpdateModelView

    def __init__(
        self,
        path_parameters: ArgOrCallable[PathParameters, TestCaseType],
        payloads: ArgOrCallable[Payloads, TestCaseType],
        headers: Optional[ArgOrCallable[Headers, TestCaseType]] = None,
    ) -> None:
        super().__init__(model_view_class=UpdateModelView)
        self.view_test_manager = ViewTestManager(
            perform_request=self.perform_request,
            path_parameters=path_parameters,
            headers=headers,
            payloads=payloads,
        )

    def perform_request(
        self,
        path_parameters: dict,
        query_parameters: dict,
        headers: dict,
        payload: dict,
    ) -> HttpResponse:
        base_path = self.model_viewset_test_case.base_path.strip("/")
        endpoint_path = self.model_view.path.lstrip("/")
        path = f"/{base_path}/{endpoint_path}"
        return self.model_viewset_test_case.client_class().generic(
            method=self.model_view.method.value,
            path=path.format(**path_parameters),
            data=json.dumps(payload),
            content_type="application/json",
            **headers,
        )

    def on_successful_request(
        self,
        response: HttpResponse,
        path_parameters: dict,
        query_parameters: dict,
        headers: dict,
        payload: dict,
    ):
        content = json.loads(response.content)

        TestAssertionHelper.assert_content_equals_schema(
            test_case=self.model_viewset_test_case,
            content=content,
            queryset=self.model_viewset_test_case.model_viewset_class.model.objects.get_queryset(),
            schema_class=self.model_view.output_schema,
        )

    def on_failed_request(
        self,
        response: HttpResponse,
        path_parameters: dict,
        query_parameters: dict,
        headers: dict,
        payload: dict,
    ):
        pass

    @tag("update")
    def test_update_model_ok(self):
        self.view_test_manager.test_view_ok(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_successful_request,
            status=HTTPStatus.OK,
        )

    @tag("update")
    def test_update_model_bad_request(self):
        self.view_test_manager.test_view_payloads_bad_request(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )

    @tag("update")
    def test_update_model_conflict(self):
        self.view_test_manager.test_view_payloads_conflict(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )

    @tag("update")
    def test_update_model_unauthorized(self):
        self.view_test_manager.test_view_headers_unauthorized(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )

    @tag("update")
    def test_update_model_forbidden(self):
        self.view_test_manager.test_view_headers_forbidden(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )

    @tag("update")
    def test_update_model_not_found(self):
        self.view_test_manager.test_view_path_parameters_not_found(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )
