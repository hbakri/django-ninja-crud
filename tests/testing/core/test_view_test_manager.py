import django.test
from django.http import HttpResponse

from ninja_crud.testing.core import ViewTestManager
from ninja_crud.testing.core.components import (
    Headers,
    PathParameters,
    Payloads,
    QueryParameters,
)


class TestViewTestManager(django.test.TestCase):
    def assertPathParametersEqual(self, first: PathParameters, second: PathParameters):
        self.assertEqual(first.ok, second.ok)
        self.assertEqual(first.not_found, second.not_found)

    @staticmethod
    def simulate_request(
        path_parameters: dict,
        query_parameters: dict,
        request_headers: dict,
        request_body: dict,
    ) -> HttpResponse:
        return HttpResponse()

    def test_simulate_request(self):
        self.assertIsInstance(self.simulate_request({}, {}, {}, {}), HttpResponse)

    def test_get_path_parameters_constant(self):
        path_parameters = PathParameters(ok={"id": 1})
        view_test_manager = ViewTestManager(
            simulate_request=self.simulate_request,
            path_parameters=path_parameters,
        )
        self.assertPathParametersEqual(
            view_test_manager.get_path_parameters(self), path_parameters
        )

    def test_get_path_parameters_callable(self):
        def get_path_parameters(test_case):
            return PathParameters(ok={"id": 1})

        view_test_manager = ViewTestManager(
            simulate_request=self.simulate_request,
            path_parameters=get_path_parameters,
        )
        self.assertPathParametersEqual(
            view_test_manager.get_path_parameters(self), get_path_parameters(self)
        )

    def test_get_path_parameters_none(self):
        view_test_manager = ViewTestManager(
            simulate_request=self.simulate_request,
        )
        self.assertPathParametersEqual(
            view_test_manager.get_path_parameters(self), PathParameters(ok={})
        )

    def test_get_path_parameters_property(self):
        path_parameters = property(lambda test_case: PathParameters(ok={"id": 1}))
        view_test_manager = ViewTestManager(
            simulate_request=self.simulate_request,
            path_parameters=path_parameters,
        )
        self.assertPathParametersEqual(
            view_test_manager.get_path_parameters(self), PathParameters(ok={"id": 1})
        )

    def test_get_path_parameters_type_error(self):
        path_parameters = "string"
        view_test_manager = ViewTestManager(
            simulate_request=self.simulate_request,
            path_parameters=path_parameters,  # type: ignore
        )
        with self.assertRaises(TypeError):
            view_test_manager.get_path_parameters(self)

    def assertQueryParametersEqual(
        self, first: QueryParameters, second: QueryParameters
    ):
        self.assertEqual(first.ok, second.ok)
        self.assertEqual(first.bad_request, second.bad_request)

    def test_get_query_parameters_constant(self):
        query_parameters = QueryParameters(ok={"page": 1})
        view_test_manager = ViewTestManager(
            simulate_request=self.simulate_request,
            query_parameters=query_parameters,
        )
        self.assertQueryParametersEqual(
            view_test_manager.get_query_parameters(self), query_parameters
        )

    def test_get_query_parameters_callable(self):
        def get_query_parameters(test_case):
            return QueryParameters(ok={"page": 1})

        view_test_manager = ViewTestManager(
            simulate_request=self.simulate_request,
            query_parameters=get_query_parameters,
        )
        self.assertQueryParametersEqual(
            view_test_manager.get_query_parameters(self), get_query_parameters(self)
        )

    def test_get_query_parameters_none(self):
        view_test_manager = ViewTestManager(
            simulate_request=self.simulate_request,
        )
        self.assertQueryParametersEqual(
            view_test_manager.get_query_parameters(self), QueryParameters(ok={})
        )

    def test_get_query_parameters_property(self):
        query_parameters = property(lambda test_case: QueryParameters(ok={"page": 1}))
        view_test_manager = ViewTestManager(
            simulate_request=self.simulate_request,
            query_parameters=query_parameters,
        )
        self.assertQueryParametersEqual(
            view_test_manager.get_query_parameters(self),
            QueryParameters(ok={"page": 1}),
        )

    def test_get_query_parameters_type_error(self):
        query_parameters = "string"
        view_test_manager = ViewTestManager(
            simulate_request=self.simulate_request,
            query_parameters=query_parameters,  # type: ignore
        )
        with self.assertRaises(TypeError):
            view_test_manager.get_query_parameters(self)

    def assertPayloadsEqual(self, first: Payloads, second: Payloads):
        self.assertEqual(first.ok, second.ok)
        self.assertEqual(first.bad_request, second.bad_request)
        self.assertEqual(first.conflict, second.conflict)

    def test_get_payloads_constant(self):
        payloads = Payloads(ok={"name": "item 1"})
        view_test_manager = ViewTestManager(
            simulate_request=self.simulate_request,
            payloads=payloads,
        )
        self.assertPayloadsEqual(view_test_manager.get_payloads(self), payloads)

    def test_get_payloads_callable(self):
        def get_payloads(test_case):
            return Payloads(ok={"name": "item 1"})

        view_test_manager = ViewTestManager(
            simulate_request=self.simulate_request,
            payloads=get_payloads,
        )
        self.assertPayloadsEqual(
            view_test_manager.get_payloads(self), get_payloads(self)
        )

    def test_get_payloads_none(self):
        view_test_manager = ViewTestManager(
            simulate_request=self.simulate_request,
        )
        self.assertPayloadsEqual(view_test_manager.get_payloads(self), Payloads(ok={}))

    def test_get_payloads_property(self):
        payloads = property(lambda test_case: Payloads(ok={"name": "item 1"}))
        view_test_manager = ViewTestManager(
            simulate_request=self.simulate_request,
            payloads=payloads,
        )
        self.assertPayloadsEqual(
            view_test_manager.get_payloads(self), Payloads(ok={"name": "item 1"})
        )

    def test_get_payloads_type_error(self):
        payloads = "string"
        view_test_manager = ViewTestManager(
            simulate_request=self.simulate_request,
            payloads=payloads,  # type: ignore
        )
        with self.assertRaises(TypeError):
            view_test_manager.get_payloads(self)

    def assertHeadersEqual(self, first: Headers, second: Headers):
        self.assertEqual(first.ok, second.ok)
        self.assertEqual(first.forbidden, second.forbidden)
        self.assertEqual(first.unauthorized, second.unauthorized)

    def test_get_headers_constant(self):
        headers = Headers(ok={"header": "value"})
        view_test_manager = ViewTestManager(
            simulate_request=self.simulate_request,
            headers=headers,
        )
        self.assertHeadersEqual(view_test_manager.get_headers(self), headers)

    def test_get_headers_callable(self):
        def get_headers(test_case):
            return Headers(ok={"header": "value"})

        view_test_manager = ViewTestManager(
            simulate_request=self.simulate_request,
            headers=get_headers,
        )
        self.assertHeadersEqual(view_test_manager.get_headers(self), get_headers(self))

    def test_get_headers_none(self):
        view_test_manager = ViewTestManager(
            simulate_request=self.simulate_request,
        )
        self.assertHeadersEqual(view_test_manager.get_headers(self), Headers(ok={}))

    def test_get_headers_property(self):
        headers = property(lambda test_case: Headers(ok={"header": "value"}))
        view_test_manager = ViewTestManager(
            simulate_request=self.simulate_request,
            headers=headers,
        )
        self.assertHeadersEqual(
            view_test_manager.get_headers(self), Headers(ok={"header": "value"})
        )

    def test_get_headers_type_error(self):
        headers = "string"
        view_test_manager = ViewTestManager(
            simulate_request=self.simulate_request,
            headers=headers,  # type: ignore
        )
        with self.assertRaises(TypeError):
            view_test_manager.get_headers(self)
