import json
from http import HTTPStatus
from typing import Optional

from django.http import HttpResponse
from django.test import tag

from ninja_crud.testing.core import ArgOrCallable, TestCaseType, ViewTestManager
from ninja_crud.testing.core.components import Headers, PathParameters, Payloads
from ninja_crud.testing.views import AbstractModelViewTest
from ninja_crud.views.create_model_view import CreateModelView


class CreateModelViewTest(AbstractModelViewTest):
    model_view: CreateModelView

    def __init__(
        self,
        payloads: ArgOrCallable[Payloads, TestCaseType],
        path_parameters: Optional[ArgOrCallable[PathParameters, TestCaseType]] = None,
        headers: Optional[ArgOrCallable[Headers, TestCaseType]] = None,
    ) -> None:
        super().__init__(model_view_class=CreateModelView)
        self.view_test_manager = ViewTestManager(
            handle_request=self.handle_request,
            path_parameters=path_parameters,
            headers=headers,
            payloads=payloads,
        )

    def on_successful_request(
        self,
        response: HttpResponse,
        path_parameters: dict,
        query_parameters: dict,
        headers: dict,
        payload: dict,
    ):
        if self.model_view.detail:
            model_class = self.model_view._related_model_class
        else:
            model_class = self.model_viewset_test_case.model_viewset_class.model

        content = json.loads(response.content)
        self.model_viewset_test_case.assertIsInstance(content, dict)
        self.model_viewset_test_case.assertIn("id", content)

        model = model_class.objects.get(id=content["id"])
        schema = self.model_view.output_schema.from_orm(model)
        self.model_viewset_test_case.assertDictEqual(content, json.loads(schema.json()))

    @tag("create")
    def test_create_model_ok(self):
        self.view_test_manager.test_view_ok(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_successful_request,
            status=HTTPStatus.CREATED,
        )

    @tag("create")
    def test_create_model_bad_request(self):
        self.view_test_manager.test_view_payloads_bad_request(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )

    @tag("create")
    def test_create_model_conflict(self):
        self.view_test_manager.test_view_payloads_conflict(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )

    @tag("create")
    def test_create_model_unauthorized(self):
        self.view_test_manager.test_view_headers_unauthorized(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )

    @tag("create")
    def test_create_model_forbidden(self):
        self.view_test_manager.test_view_headers_forbidden(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )

    @tag("create")
    def test_create_model_not_found(self):
        self.view_test_manager.test_view_path_parameters_not_found(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )
