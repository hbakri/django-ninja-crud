from http import HTTPStatus
from typing import Callable, List, Optional, TypeVar, Union

from django.http import HttpResponse
from django.test import TestCase

from ninja_crud.testing.core.components import (
    Headers,
    PathParameters,
    Payloads,
    QueryParameters,
)

T = TypeVar("T")
TestCaseType = TypeVar("TestCaseType", bound=TestCase)
ArgOrCallable = Union[T, property, Callable[[TestCaseType], T]]
CompletionCallback = Callable[[HttpResponse, dict, dict, dict, dict], None]


class ViewTestManager:
    def __init__(
        self,
        handle_request: Callable[[dict, dict, dict, dict], HttpResponse],
        path_parameters: Optional[ArgOrCallable[PathParameters, TestCaseType]] = None,
        query_parameters: Optional[ArgOrCallable[QueryParameters, TestCaseType]] = None,
        headers: Optional[ArgOrCallable[Headers, TestCaseType]] = None,
        payloads: Optional[ArgOrCallable[Payloads, TestCaseType]] = None,
    ) -> None:
        self.handle_request = handle_request
        self.path_parameters = path_parameters or PathParameters(ok={})
        self.query_parameters = query_parameters or QueryParameters(ok={})
        self.headers = headers or Headers(ok={})
        self.payloads = payloads or Payloads(ok={})

    @staticmethod
    def _get_arg_or_callable(
        test_case: TestCase, params: ArgOrCallable[T, TestCaseType]
    ) -> T:
        if callable(params):
            return params(test_case)
        elif isinstance(params, property):
            return params.fget(test_case)
        else:
            return params

    def get_path_parameters(self, test_case: TestCase) -> PathParameters:
        path_parameters = self._get_arg_or_callable(test_case, self.path_parameters)
        if not isinstance(path_parameters, PathParameters):
            raise TypeError(
                f"Expected 'path_parameters' to be an instance of 'PathParameters', "
                f"but got {type(path_parameters)}"
            )
        return path_parameters

    def get_query_parameters(self, test_case: TestCase) -> QueryParameters:
        query_parameters = self._get_arg_or_callable(test_case, self.query_parameters)
        if not isinstance(query_parameters, QueryParameters):
            raise TypeError(
                f"Expected 'query_parameters' to be an instance of 'QueryParameters', "
                f"but got {type(query_parameters)}"
            )
        return query_parameters

    def get_headers(self, test_case: TestCase) -> Headers:
        headers = self._get_arg_or_callable(test_case, self.headers)
        if not isinstance(headers, Headers):
            raise TypeError(
                f"Expected 'headers' to be an instance of 'Headers', "
                f"but got {type(headers)}"
            )
        return headers

    def get_payloads(self, test_case: TestCase) -> Payloads:
        payloads = self._get_arg_or_callable(test_case, self.payloads)
        if not isinstance(payloads, Payloads):
            raise TypeError(
                f"Expected 'payloads' to be an instance of 'Payloads', "
                f"but got {type(payloads)}"
            )
        return payloads

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
            headers: dict,
            payload: dict,
        ):
            test_case.assertEqual(response.status_code, status)
            on_completion(response, path_parameters, query_parameters, headers, payload)

        return on_completion_with_status_check

    def run_combinatorial_tests(
        self,
        test_case: TestCase,
        path_parameters_list: List[dict],
        query_parameters_list: List[dict],
        headers_list: List[dict],
        payload_list: List[dict],
        on_completion: CompletionCallback,
    ):
        for path_parameters in path_parameters_list:
            for query_parameters in query_parameters_list:
                for headers in headers_list:
                    for payload in payload_list:
                        with test_case.subTest(
                            path_parameters=path_parameters,
                            query_parameters=query_parameters,
                            headers=headers,
                            payload=payload,
                        ):
                            response = self.handle_request(
                                path_parameters, query_parameters, headers, payload
                            )
                            on_completion(
                                response,
                                path_parameters,
                                query_parameters,
                                headers,
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
        headers = self.get_headers(test_case)
        payloads = self.get_payloads(test_case)
        self.run_combinatorial_tests(
            test_case=test_case,
            path_parameters_list=path_parameters.ok,
            query_parameters_list=query_parameters.ok,
            headers_list=headers.ok,
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
        headers = self.get_headers(test_case)
        payloads = self.get_payloads(test_case)
        if payloads.bad_request is None:
            test_case.skipTest(reason="No 'bad_request' payload provided")
        self.run_combinatorial_tests(
            test_case=test_case,
            path_parameters_list=path_parameters.ok,
            query_parameters_list=query_parameters.ok,
            headers_list=headers.ok,
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
        headers = self.get_headers(test_case)
        payloads = self.get_payloads(test_case)
        if payloads.conflict is None:
            test_case.skipTest(reason="No 'conflict' payload provided")
        self.run_combinatorial_tests(
            test_case=test_case,
            path_parameters_list=path_parameters.ok,
            query_parameters_list=query_parameters.ok,
            headers_list=headers.ok,
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
        headers = self.get_headers(test_case)
        payloads = self.get_payloads(test_case)
        if query_parameters.bad_request is None:
            test_case.skipTest(reason="No 'bad_request' query parameters provided")
        self.run_combinatorial_tests(
            test_case=test_case,
            path_parameters_list=path_parameters.ok,
            query_parameters_list=query_parameters.bad_request,
            headers_list=headers.ok,
            payload_list=payloads.ok,
            on_completion=self.wrap_completion_with_status_check(
                test_case, on_completion=on_completion, status=status
            ),
        )

    def test_view_headers_unauthorized(
        self,
        test_case: TestCase,
        on_completion: CompletionCallback,
        status: HTTPStatus = HTTPStatus.UNAUTHORIZED,
    ):
        path_parameters = self.get_path_parameters(test_case)
        query_parameters = self.get_query_parameters(test_case)
        headers = self.get_headers(test_case)
        payloads = self.get_payloads(test_case)
        if headers.unauthorized is None:
            test_case.skipTest(reason="No 'unauthorized' headers provided")
        self.run_combinatorial_tests(
            test_case=test_case,
            path_parameters_list=path_parameters.ok,
            query_parameters_list=query_parameters.ok,
            headers_list=headers.unauthorized,
            payload_list=payloads.ok,
            on_completion=self.wrap_completion_with_status_check(
                test_case, on_completion=on_completion, status=status
            ),
        )

    def test_view_headers_forbidden(
        self,
        test_case: TestCase,
        on_completion: CompletionCallback,
        status: HTTPStatus = HTTPStatus.FORBIDDEN,
    ):
        path_parameters = self.get_path_parameters(test_case)
        query_parameters = self.get_query_parameters(test_case)
        headers = self.get_headers(test_case)
        payloads = self.get_payloads(test_case)
        if headers.forbidden is None:
            test_case.skipTest(reason="No 'forbidden' headers provided")
        self.run_combinatorial_tests(
            test_case=test_case,
            path_parameters_list=path_parameters.ok,
            query_parameters_list=query_parameters.ok,
            headers_list=headers.forbidden,
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
        headers = self.get_headers(test_case)
        payloads = self.get_payloads(test_case)
        if path_parameters.not_found is None:
            test_case.skipTest(reason="No 'not_found' path parameters provided")
        self.run_combinatorial_tests(
            test_case=test_case,
            path_parameters_list=path_parameters.not_found,
            query_parameters_list=query_parameters.ok,
            headers_list=headers.ok,
            payload_list=payloads.ok,
            on_completion=self.wrap_completion_with_status_check(
                test_case, on_completion=on_completion, status=status
            ),
        )
