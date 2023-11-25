import json
from http import HTTPStatus
from typing import Optional

from django.http import HttpRequest, HttpResponse
from django.test import tag
from ninja import FilterSchema

from ninja_crud.testing.core import ArgOrCallable, TestCaseType, ViewTestManager
from ninja_crud.testing.core.components import Headers, PathParameters, QueryParameters
from ninja_crud.testing.views import AbstractModelViewTest
from ninja_crud.testing.views.helpers import TestAssertionHelper
from ninja_crud.views.list_model_view import ListModelView


class ListModelViewTest(AbstractModelViewTest):
    model_view: ListModelView

    def __init__(
        self,
        path_parameters: Optional[ArgOrCallable[PathParameters, TestCaseType]] = None,
        query_parameters: Optional[ArgOrCallable[QueryParameters, TestCaseType]] = None,
        headers: Optional[ArgOrCallable[Headers, TestCaseType]] = None,
    ) -> None:
        super().__init__(model_view_class=ListModelView)
        self.view_test_manager = ViewTestManager(
            perform_request=self.perform_request,
            path_parameters=path_parameters,
            query_parameters=query_parameters,
            headers=headers,
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
        return self.model_viewset_test_case.client_class().get(
            path=path.format(**path_parameters),
            data=query_parameters,
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

        limit = query_parameters.pop("limit", 100)
        offset = query_parameters.pop("offset", 0)
        if self.model_view.filter_schema is not None:
            filters = self.model_view.filter_schema(**query_parameters)
        else:
            filters = FilterSchema()

        queryset = self.model_view.list_models(
            request=HttpRequest(),
            id=path_parameters["id"] if self.model_view.detail else None,
            filters=filters,
            model_class=self.model_viewset_test_case.model_viewset_class.model,
        )

        TestAssertionHelper.assert_content_equals_schema_list(
            test_case=self.model_viewset_test_case,
            content=content,
            queryset=queryset,
            schema_class=self.model_view.output_schema,
            limit=limit,
            offset=offset,
            pagination_class=self.model_view.pagination_class,
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

    @tag("list")
    def test_list_model_ok(self):
        self.view_test_manager.test_view_ok(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_successful_request,
            status=HTTPStatus.OK,
        )

    @tag("list")
    def test_list_model_bad_request(self):
        self.view_test_manager.test_view_query_parameters_bad_request(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )

    @tag("list")
    def test_list_model_unauthorized(self):
        self.view_test_manager.test_view_headers_unauthorized(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )

    @tag("list")
    def test_list_model_forbidden(self):
        self.view_test_manager.test_view_headers_forbidden(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )

    @tag("list")
    def test_list_model_not_found(self):
        self.view_test_manager.test_view_path_parameters_not_found(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )
