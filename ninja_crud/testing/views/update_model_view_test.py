import http
import json
from typing import Optional

import django.http
import django.test

from ninja_crud import views
from ninja_crud.testing.core import ArgOrCallable, TestCaseType, ViewTestManager
from ninja_crud.testing.core.components import Headers, PathParameters, Payloads
from ninja_crud.testing.views import AbstractModelViewTest


class UpdateModelViewTest(AbstractModelViewTest):
    model_view: views.UpdateModelView

    def __init__(
        self,
        path_parameters: ArgOrCallable[PathParameters, TestCaseType],
        payloads: ArgOrCallable[Payloads, TestCaseType],
        headers: Optional[ArgOrCallable[Headers, TestCaseType]] = None,
    ) -> None:
        super().__init__(model_view_class=views.UpdateModelView)
        self.view_test_manager = ViewTestManager(
            handle_request=self.handle_request,
            path_parameters=path_parameters,
            headers=headers,
            payloads=payloads,
        )

    def on_successful_request(
        self,
        response: django.http.HttpResponse,
        path_parameters: dict,
        query_parameters: dict,
        headers: dict,
        payload: dict,
    ) -> None:
        model = self.model_viewset_test_case.model_viewset_class.model.objects.get(
            id=path_parameters["id"]
        )
        schema = self.model_view.output_schema.from_orm(model)

        content = json.loads(response.content)
        self.model_viewset_test_case.assertDictEqual(content, json.loads(schema.json()))

    def on_failed_request(
        self,
        response: django.http.HttpResponse,
        path_parameters: dict,
        query_parameters: dict,
        headers: dict,
        payload: dict,
    ) -> None:
        pass

    @django.test.tag("update")
    def test_update_model_ok(self):
        self.view_test_manager.test_view_ok(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_successful_request,
            status=http.HTTPStatus.OK,
        )

    @django.test.tag("update")
    def test_update_model_bad_request(self):
        self.view_test_manager.test_view_payloads_bad_request(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )

    @django.test.tag("update")
    def test_update_model_conflict(self):
        self.view_test_manager.test_view_payloads_conflict(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )

    @django.test.tag("update")
    def test_update_model_unauthorized(self):
        self.view_test_manager.test_view_headers_unauthorized(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )

    @django.test.tag("update")
    def test_update_model_forbidden(self):
        self.view_test_manager.test_view_headers_forbidden(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )

    @django.test.tag("update")
    def test_update_model_not_found(self):
        self.view_test_manager.test_view_path_parameters_not_found(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )
