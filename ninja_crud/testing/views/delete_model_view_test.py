import http
from typing import Optional

import django.http
import django.test
from django.core.exceptions import ObjectDoesNotExist

from ninja_crud import views
from ninja_crud.testing.core import ArgOrCallable, TestCaseType, ViewTestManager
from ninja_crud.testing.core.components import Headers, PathParameters
from ninja_crud.testing.views import AbstractModelViewTest


class DeleteModelViewTest(AbstractModelViewTest):
    model_view: views.DeleteModelView

    def __init__(
        self,
        path_parameters: ArgOrCallable[PathParameters, TestCaseType],
        headers: Optional[ArgOrCallable[Headers, TestCaseType]] = None,
    ) -> None:
        super().__init__(model_view_class=views.DeleteModelView)
        self.view_test_manager = ViewTestManager(
            handle_request=self.handle_request,
            path_parameters=path_parameters,
            headers=headers,
        )

    def on_successful_request(
        self,
        response: django.http.HttpResponse,
        path_parameters: dict,
        query_parameters: dict,
        headers: dict,
        payload: dict,
    ):
        self.model_viewset_test_case.assertEqual(response.content, b"")

        model_class = self.model_viewset_test_case.model_viewset_class.model
        with self.model_viewset_test_case.assertRaises(ObjectDoesNotExist):
            model_class.objects.get(id=path_parameters["id"])

    def on_failed_request(
        self,
        response: django.http.HttpResponse,
        path_parameters: dict,
        query_parameters: dict,
        headers: dict,
        payload: dict,
    ):
        pass

    @django.test.tag("delete")
    def test_delete_model_ok(self):
        self.view_test_manager.test_view_ok(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_successful_request,
            status=http.HTTPStatus.NO_CONTENT,
        )

    @django.test.tag("delete")
    def test_delete_model_unauthorized(self):
        self.view_test_manager.test_view_headers_unauthorized(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )

    @django.test.tag("delete")
    def test_delete_model_forbidden(self):
        self.view_test_manager.test_view_headers_forbidden(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )

    @django.test.tag("delete")
    def test_delete_model_not_found(self):
        self.view_test_manager.test_view_path_parameters_not_found(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )
