import json
import logging
from http import HTTPStatus

from django.http import HttpResponse
from django.test import tag

from ninja_crud.tests import QueryParameters
from ninja_crud.tests.assertion_helper import TestAssertionHelper
from ninja_crud.tests.request_components import AuthHeaders, PathParameters
from ninja_crud.tests.request_composer import (
    ArgOrCallable,
    RequestComposer,
    TestCaseType,
)
from ninja_crud.tests.test_abstract import AbstractTestModelView
from ninja_crud.views.list import ListModelView

logger = logging.getLogger(__name__)


class TestListModelView(AbstractTestModelView):
    model_view_class = ListModelView
    model_view: ListModelView

    def __init__(
        self,
        path_parameters: ArgOrCallable[PathParameters, TestCaseType] = None,
        query_parameters: ArgOrCallable[QueryParameters, TestCaseType] = None,
        auth_headers: ArgOrCallable[AuthHeaders, TestCaseType] = None,
    ) -> None:
        self.request_composer = RequestComposer(
            request_method=self.request_list_model,
            path_parameters=path_parameters,
            query_parameters=query_parameters,
            auth_headers=auth_headers,
        )

    def request_list_model(
        self,
        path_parameters: dict,
        query_parameters: dict,
        auth_headers: dict,
        payload: dict,
    ) -> HttpResponse:
        path = "/" + self.test_model_view_set.base_path + self.model_view.get_path()
        response = self.test_model_view_set.client_class().get(
            path=path.format(**path_parameters),
            data=query_parameters,
            content_type="application/json",
            **auth_headers,
        )
        return response

    def assert_response_is_ok(
        self, response: HttpResponse, query_parameters: dict, path_parameters: dict
    ):
        self.test_model_view_set.assertEqual(response.status_code, HTTPStatus.OK)
        content = json.loads(response.content)

        queryset = self.model_view._get_queryset(
            self.test_model_view_set.model_view_set_class.model_class,
            path_parameters["id"] if "id" in path_parameters else None,
        )

        limit = query_parameters.pop("limit", 100)
        offset = query_parameters.pop("offset", 0)
        if self.model_view.filter_schema is not None:
            filters = self.model_view.filter_schema(**query_parameters)
            queryset = self.model_view._filter_queryset(queryset, filters)

        TestAssertionHelper.assert_content_equals_schema_list(
            test_case=self.test_model_view_set,
            content=content,
            queryset=queryset,
            schema_class=self.model_view.output_schema,
            limit=limit,
            offset=offset,
        )

    def assert_response_is_bad_request(
        self, response: HttpResponse, status_code: HTTPStatus
    ):
        TestAssertionHelper.assert_response_is_bad_request(
            self.test_model_view_set, response, status_code=status_code
        )

    @tag("list")
    def test_list_model_ok(self):
        self.request_composer.test_view_ok(
            test_case=self.test_model_view_set,
            completion_callback=lambda response, path_parameters, query_parameters, _, __: self.assert_response_is_ok(
                response,
                path_parameters=path_parameters,
                query_parameters=query_parameters,
            ),
        )

    @tag("list")
    def test_list_model_bad_request(self):
        self.request_composer.test_view_query_parameters_bad_request(
            test_case=self.test_model_view_set,
            completion_callback=lambda response, _, __, ___, ____: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.BAD_REQUEST
            ),
        )

    @tag("list")
    def test_list_model_unauthorized(self):
        self.request_composer.test_view_auth_headers_unauthorized(
            test_case=self.test_model_view_set,
            completion_callback=lambda response, _, __, ___, ____: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.UNAUTHORIZED
            ),
        )

    @tag("list")
    def test_list_model_forbidden(self):
        self.request_composer.test_view_auth_headers_forbidden(
            test_case=self.test_model_view_set,
            completion_callback=lambda response, _, __, ___, ____: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.FORBIDDEN
            ),
        )

    @tag("list")
    def test_list_model_not_found(self):
        self.request_composer.test_view_path_parameters_not_found(
            test_case=self.test_model_view_set,
            completion_callback=lambda response, _, __, ___, ____: self.assert_response_is_bad_request(
                response, status_code=HTTPStatus.NOT_FOUND
            ),
        )


class ListModelViewTest(TestListModelView):
    def __init__(self, *args, **kwargs):  # pragma: no cover
        logger.warning(
            f"{ListModelViewTest.__name__} is deprecated, use {TestListModelView.__name__} instead",
            DeprecationWarning,
        )
        super().__init__(*args, **kwargs)
