import logging
from http import HTTPStatus

from django.http import HttpResponse
from django.test import tag

from ninja_crud.tests.request_components import AuthHeaders, PathParameters
from ninja_crud.tests.request_composer import (
    ArgOrCallable,
    RequestComposer,
    TestCaseType,
)
from ninja_crud.tests.test_abstract import AbstractTestModelView
from ninja_crud.views.delete import DeleteModelView

logger = logging.getLogger(__name__)


class TestDeleteModelView(AbstractTestModelView):
    model_view_class = DeleteModelView
    model_view: DeleteModelView

    def __init__(
        self,
        path_parameters: ArgOrCallable[PathParameters, TestCaseType],
        auth_headers: ArgOrCallable[AuthHeaders, TestCaseType] = None,
    ) -> None:
        self.request_composer = RequestComposer(
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
        path = "/" + self.test_model_view_set.base_path + self.model_view.get_path()
        return self.test_model_view_set.client_class().delete(
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
        self.test_model_view_set.assertEqual(
            response.status_code, HTTPStatus.NO_CONTENT
        )
        self.test_model_view_set.assertEqual(response.content, b"")

        queryset = (
            self.test_model_view_set.model_view_set_class.model_class.objects.filter(
                id=path_parameters["id"]
            )
        )
        self.test_model_view_set.assertEqual(queryset.count(), 0)

    def on_failed_request(
        self,
        response: HttpResponse,
        path_parameters: dict,
        query_parameters: dict,
        auth_headers: dict,
        payload: dict,
    ):
        pass

    @tag("delete")
    def test_delete_model_ok(self):
        self.request_composer.test_view_ok(
            test_case=self.test_model_view_set,
            on_completion=self.on_successful_request,
            status=HTTPStatus.NO_CONTENT,
        )

    @tag("delete")
    def test_delete_model_unauthorized(self):
        self.request_composer.test_view_auth_headers_unauthorized(
            test_case=self.test_model_view_set,
            on_completion=self.on_failed_request,
        )

    @tag("delete")
    def test_delete_model_forbidden(self):
        self.request_composer.test_view_auth_headers_forbidden(
            test_case=self.test_model_view_set,
            on_completion=self.on_failed_request,
        )

    @tag("delete")
    def test_delete_model_not_found(self):
        self.request_composer.test_view_path_parameters_not_found(
            test_case=self.test_model_view_set,
            on_completion=self.on_failed_request,
        )


class DeleteModelViewTest(TestDeleteModelView):
    def __init__(self, *args, **kwargs):  # pragma: no cover
        logger.warning(
            f"{DeleteModelViewTest.__name__} is deprecated, use {TestDeleteModelView.__name__} instead",
            DeprecationWarning,
        )
        super().__init__(*args, **kwargs)
