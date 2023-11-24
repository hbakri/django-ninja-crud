import json
from http import HTTPStatus
from typing import Optional

from django.http import HttpResponse
from django.test import tag

from ninja_crud.testing.core import ArgOrCallable, TestCaseType, ViewTestManager
from ninja_crud.testing.core.components import Headers, PathParameters
from ninja_crud.testing.views import AbstractModelViewTest
from ninja_crud.testing.views.helpers.test_assertion_helper import default_serializer
from ninja_crud.views.retrieve_model_view import RetrieveModelView


class RetrieveModelViewTest(AbstractModelViewTest):
    model_view: RetrieveModelView

    def __init__(
        self,
        path_parameters: ArgOrCallable[PathParameters, TestCaseType],
        headers: Optional[ArgOrCallable[Headers, TestCaseType]] = None,
    ) -> None:
        super().__init__(model_view_class=RetrieveModelView)
        self.view_test_manager = ViewTestManager(
            perform_request=self.perform_request,
            path_parameters=path_parameters,
            headers=headers,
        )

    def perform_request(
        self,
        path_parameters: dict,
        query_parameters: dict,
        headers: dict,
        payload: dict,
    ) -> HttpResponse:
        path = "/" + self.model_viewset_test_case.base_path + self.model_view.path
        return self.model_viewset_test_case.client_class().get(
            path=path.format(**path_parameters),
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
        model = self.model_view.retrieve_model(
            id=path_parameters["id"],
            model_class=self.model_viewset_test_case.model_viewset_class.model,
        )
        schema = self.model_view.output_schema.from_orm(model)

        content = json.loads(response.content)
        self.model_viewset_test_case.assertDictEqual(
            content,
            json.loads(json.dumps(schema.dict(), default=default_serializer)),
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

    @tag("retrieve")
    def test_retrieve_model_ok(self):
        self.view_test_manager.test_view_ok(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_successful_request,
            status=HTTPStatus.OK,
        )

    @tag("retrieve")
    def test_retrieve_model_unauthorized(self):
        self.view_test_manager.test_view_headers_unauthorized(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )

    @tag("retrieve")
    def test_retrieve_model_forbidden(self):
        self.view_test_manager.test_view_headers_forbidden(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )

    @tag("retrieve")
    def test_retrieve_model_not_found(self):
        self.view_test_manager.test_view_path_parameters_not_found(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )
