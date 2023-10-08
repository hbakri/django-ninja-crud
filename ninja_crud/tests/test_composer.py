from http import HTTPStatus
from typing import Callable, List, Optional, TypeVar, Union

from django.http import HttpResponse
from django.test import TestCase

from ninja_crud.tests.request_components import (
    AuthHeaders,
    PathParameters,
    Payloads,
    QueryParameters,
)

T = TypeVar("T")
TestCaseType = TypeVar("TestCaseType", bound=TestCase)
ArgOrCallable = Union[T, Callable[[TestCaseType], T]]

CompletionCallback = Callable[[HttpResponse, dict, dict, dict, dict], None]


class TestComposer:
    def __init__(
        self,
        perform_request: Callable[[dict, dict, dict, dict], HttpResponse],
        path_parameters: Optional[ArgOrCallable[PathParameters, TestCaseType]] = None,
        query_parameters: Optional[ArgOrCallable[QueryParameters, TestCaseType]] = None,
        auth_headers: Optional[ArgOrCallable[AuthHeaders, TestCaseType]] = None,
        payloads: Optional[ArgOrCallable[Payloads, TestCaseType]] = None,
    ) -> None:
        if path_parameters is None:
            path_parameters = PathParameters(ok={})
        if query_parameters is None:
            query_parameters = QueryParameters(ok={})
        if auth_headers is None:
            auth_headers = AuthHeaders(ok={})
        if payloads is None:
            payloads = Payloads(ok={})

        self.perform_request = perform_request
        self.path_parameters = path_parameters
        self.query_parameters = query_parameters
        self.auth_headers = auth_headers
        self.payloads = payloads

    @staticmethod
    def _get_arg_or_callable(
        test_case: TestCase, params: ArgOrCallable[T, TestCaseType]
    ) -> T:
        return params(test_case) if callable(params) else params

    def get_path_parameters(self, test_case: TestCase) -> PathParameters:
        return self._get_arg_or_callable(test_case, self.path_parameters)

    def get_query_parameters(self, test_case: TestCase) -> QueryParameters:
        return self._get_arg_or_callable(test_case, self.query_parameters)

    def get_auth_headers(self, test_case: TestCase) -> AuthHeaders:
        return self._get_arg_or_callable(test_case, self.auth_headers)

    def get_payloads(self, test_case: TestCase) -> Payloads:
        return self._get_arg_or_callable(test_case, self.payloads)

    @staticmethod
    def wrap_completion_with_status_check(
        test_case: TestCase,
        on_completion: CompletionCallback,
        status: HTTPStatus,
    ) -> CompletionCallback:
        def on_completion_with_status_check(
            response: HttpResponse,
            path_parameters: dict,
            query_parameters: dict,
            auth_headers: dict,
            payload: dict,
        ):
            test_case.assertEqual(response.status_code, status)
            on_completion(
                response, path_parameters, query_parameters, auth_headers, payload
            )

        return on_completion_with_status_check

    def run_combinatorial_tests(
        self,
        test_case: TestCase,
        path_parameters_list: List[dict],
        query_parameters_list: List[dict],
        auth_headers_list: List[dict],
        payload_list: List[dict],
        on_completion: CompletionCallback,
    ):
        for path_parameters in path_parameters_list:
            for query_parameters in query_parameters_list:
                for auth_headers in auth_headers_list:
                    for payload in payload_list:
                        with test_case.subTest(
                            path_parameters=path_parameters,
                            query_parameters=query_parameters,
                            auth_headers=auth_headers,
                            payload=payload,
                        ):
                            response = self.perform_request(
                                path_parameters, query_parameters, auth_headers, payload
                            )
                            on_completion(
                                response,
                                path_parameters,
                                query_parameters,
                                auth_headers,
                                payload,
                            )

    def test_view_ok(
        self,
        test_case: TestCase,
        on_completion: CompletionCallback,
        status: HTTPStatus = HTTPStatus.OK,
    ):
        path_parameters = self.get_path_parameters(test_case)
        query_parameters = self.get_query_parameters(test_case)
        auth_headers = self.get_auth_headers(test_case)
        payloads = self.get_payloads(test_case)
        self.run_combinatorial_tests(
            test_case=test_case,
            path_parameters_list=path_parameters.ok,
            query_parameters_list=query_parameters.ok,
            auth_headers_list=auth_headers.ok,
            payload_list=payloads.ok,
            on_completion=self.wrap_completion_with_status_check(
                test_case, on_completion=on_completion, status=status
            ),
        )

    def test_view_payloads_bad_request(
        self,
        test_case: TestCase,
        on_completion: CompletionCallback,
        status: HTTPStatus = HTTPStatus.BAD_REQUEST,
    ):
        path_parameters = self.get_path_parameters(test_case)
        query_parameters = self.get_query_parameters(test_case)
        auth_headers = self.get_auth_headers(test_case)
        payloads = self.get_payloads(test_case)
        if payloads.bad_request is None:
            test_case.skipTest("No 'bad_request' payload provided")
        self.run_combinatorial_tests(
            test_case=test_case,
            path_parameters_list=path_parameters.ok,
            query_parameters_list=query_parameters.ok,
            auth_headers_list=auth_headers.ok,
            payload_list=payloads.bad_request,
            on_completion=self.wrap_completion_with_status_check(
                test_case, on_completion=on_completion, status=status
            ),
        )

    def test_view_payloads_conflict(
        self,
        test_case: TestCase,
        on_completion: CompletionCallback,
        status: HTTPStatus = HTTPStatus.CONFLICT,
    ):
        path_parameters = self.get_path_parameters(test_case)
        query_parameters = self.get_query_parameters(test_case)
        auth_headers = self.get_auth_headers(test_case)
        payloads = self.get_payloads(test_case)
        if payloads.conflict is None:
            test_case.skipTest("No 'conflict' payload provided")
        self.run_combinatorial_tests(
            test_case=test_case,
            path_parameters_list=path_parameters.ok,
            query_parameters_list=query_parameters.ok,
            auth_headers_list=auth_headers.ok,
            payload_list=payloads.conflict,
            on_completion=self.wrap_completion_with_status_check(
                test_case, on_completion=on_completion, status=status
            ),
        )

    def test_view_query_parameters_bad_request(
        self,
        test_case: TestCase,
        on_completion: CompletionCallback,
        status: HTTPStatus = HTTPStatus.BAD_REQUEST,
    ):
        path_parameters = self.get_path_parameters(test_case)
        query_parameters = self.get_query_parameters(test_case)
        auth_headers = self.get_auth_headers(test_case)
        payloads = self.get_payloads(test_case)
        if query_parameters.bad_request is None:
            test_case.skipTest("No 'bad_request' query parameters provided")
        self.run_combinatorial_tests(
            test_case=test_case,
            path_parameters_list=path_parameters.ok,
            query_parameters_list=query_parameters.bad_request,
            auth_headers_list=auth_headers.ok,
            payload_list=payloads.ok,
            on_completion=self.wrap_completion_with_status_check(
                test_case, on_completion=on_completion, status=status
            ),
        )

    def test_view_auth_headers_unauthorized(
        self,
        test_case: TestCase,
        on_completion: CompletionCallback,
        status: HTTPStatus = HTTPStatus.UNAUTHORIZED,
    ):
        path_parameters = self.get_path_parameters(test_case)
        query_parameters = self.get_query_parameters(test_case)
        auth_headers = self.get_auth_headers(test_case)
        payloads = self.get_payloads(test_case)
        if auth_headers.unauthorized is None:
            test_case.skipTest("No 'unauthorized' auth headers provided")
        self.run_combinatorial_tests(
            test_case=test_case,
            path_parameters_list=path_parameters.ok,
            query_parameters_list=query_parameters.ok,
            auth_headers_list=auth_headers.unauthorized,
            payload_list=payloads.ok,
            on_completion=self.wrap_completion_with_status_check(
                test_case, on_completion=on_completion, status=status
            ),
        )

    def test_view_auth_headers_forbidden(
        self,
        test_case: TestCase,
        on_completion: CompletionCallback,
        status: HTTPStatus = HTTPStatus.FORBIDDEN,
    ):
        path_parameters = self.get_path_parameters(test_case)
        query_parameters = self.get_query_parameters(test_case)
        auth_headers = self.get_auth_headers(test_case)
        payloads = self.get_payloads(test_case)
        if auth_headers.forbidden is None:
            test_case.skipTest("No 'forbidden' auth headers provided")
        self.run_combinatorial_tests(
            test_case=test_case,
            path_parameters_list=path_parameters.ok,
            query_parameters_list=query_parameters.ok,
            auth_headers_list=auth_headers.forbidden,
            payload_list=payloads.ok,
            on_completion=self.wrap_completion_with_status_check(
                test_case, on_completion=on_completion, status=status
            ),
        )

    def test_view_path_parameters_not_found(
        self,
        test_case: TestCase,
        on_completion: CompletionCallback,
        status: HTTPStatus = HTTPStatus.NOT_FOUND,
    ):
        path_parameters = self.get_path_parameters(test_case)
        query_parameters = self.get_query_parameters(test_case)
        auth_headers = self.get_auth_headers(test_case)
        payloads = self.get_payloads(test_case)
        if path_parameters.not_found is None:
            test_case.skipTest("No 'not_found' path parameters provided")
        self.run_combinatorial_tests(
            test_case=test_case,
            path_parameters_list=path_parameters.not_found,
            query_parameters_list=query_parameters.ok,
            auth_headers_list=auth_headers.ok,
            payload_list=payloads.ok,
            on_completion=self.wrap_completion_with_status_check(
                test_case, on_completion=on_completion, status=status
            ),
        )
