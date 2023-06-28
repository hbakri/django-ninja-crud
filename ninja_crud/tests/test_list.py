import json
from http import HTTPStatus

from django.http import HttpResponse
from django.urls import reverse

from ninja_crud.tests import QueryParams
from ninja_crud.tests.test_abstract import (
    AbstractModelViewTest,
    AuthParams,
    ParamsOrCallable,
    PathParams,
    TestCaseType,
)
from ninja_crud.views.list import ListModelView


class ListModelViewTest(AbstractModelViewTest):
    model_view = ListModelView

    def __init__(
        self,
        path_params: ParamsOrCallable[PathParams, TestCaseType] = None,
        auth_params: ParamsOrCallable[AuthParams, TestCaseType] = None,
        query_params: ParamsOrCallable[QueryParams, TestCaseType] = None,
    ) -> None:
        if path_params is None:
            path_params = PathParams(ok={})
        super().__init__(path_params=path_params, auth_params=auth_params)
        self.query_params = query_params

    def get_query_params(self) -> QueryParams:
        if callable(self.query_params):
            return self.query_params(self.test_case)
        return self.query_params

    def request_list_model(
        self, path_params: dict, auth_params: dict, query_params: dict = None
    ) -> HttpResponse:
        model_view: ListModelView = self.get_model_view()
        url_name = model_view.get_url_name(self.model_view_set.model)
        response = self.client.get(
            reverse(f"api:{url_name}", kwargs=path_params),
            data=query_params if query_params is not None else {},
            content_type="application/json",
            **auth_params,
        )
        return response

    def assert_response_is_ok(
        self, response: HttpResponse, path_params: dict, query_params: dict = None
    ):
        self.test_case.assertEqual(response.status_code, HTTPStatus.OK)
        content = json.loads(response.content)

        model_view: ListModelView = self.get_model_view()
        if model_view.detail:
            queryset = model_view.get_queryset(
                self.model_view_set.model, path_params["id"]
            )
        else:
            queryset = model_view.get_queryset(self.model_view_set.model)

        if query_params is not None:
            limit = query_params.pop("limit", 100)
            offset = query_params.pop("offset", 0)
            filter_instance = model_view.filter_schema(**query_params)
            queryset = model_view.filter_queryset(queryset, filter_instance)
        else:
            limit = 100
            offset = 0

        self.assert_content_equals_schema_list(
            content,
            queryset=queryset,
            output_schema=model_view.output_schema,
            limit=limit,
            offset=offset,
        )

    def test_list_model_ok(self):
        path_params = self.get_path_params()
        response = self.request_list_model(
            path_params=path_params.ok,
            auth_params=self.get_auth_params().ok,
        )
        self.assert_response_is_ok(response, path_params.ok)

    def test_list_model_ok_with_query_params(self):
        query_params = self.get_query_params()
        if query_params is None:
            self.test_case.skipTest("No ok query provided")
        path_params = self.get_path_params()
        response = self.request_list_model(
            path_params=path_params.ok,
            auth_params=self.get_auth_params().ok,
            query_params=query_params.ok,
        )
        self.assert_response_is_ok(response, path_params.ok, query_params.ok)

    def test_list_model_bad_request_with_query_params(self):
        query_params = self.get_query_params()
        if query_params is None or query_params.bad_request is None:
            self.test_case.skipTest("No bad request query provided")
        response = self.request_list_model(
            path_params=self.get_path_params().ok,
            auth_params=self.get_auth_params().ok,
            query_params=query_params.bad_request,
        )
        self.assert_response_is_bad_request(
            response, status_code=HTTPStatus.BAD_REQUEST
        )

    def test_list_model_unauthorized(self):
        auth_params = self.get_auth_params()
        if auth_params.unauthorized is None:
            self.test_case.skipTest("No unauthorized auth provided")
        response = self.request_list_model(
            path_params=self.get_path_params().ok,
            auth_params=auth_params.unauthorized,
        )
        self.assert_response_is_bad_request(
            response, status_code=HTTPStatus.UNAUTHORIZED
        )

    def test_list_model_forbidden(self):
        auth_params = self.get_auth_params()
        if auth_params.forbidden is None:
            self.test_case.skipTest("No forbidden auth provided")
        response = self.request_list_model(
            path_params=self.get_path_params().ok,
            auth_params=auth_params.forbidden,
        )
        self.assert_response_is_bad_request(response, status_code=HTTPStatus.FORBIDDEN)
