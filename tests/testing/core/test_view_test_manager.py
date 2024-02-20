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

    def test_get_path_parameters_constant(self):
        path_parameters = PathParameters(ok={"id": 1})
        view_test_manager = ViewTestManager(
            simulate_request=lambda *args, **kwargs: HttpResponse(),
            path_parameters=path_parameters,
        )
        self.assertPathParametersEqual(
            view_test_manager.get_path_parameters(self), path_parameters
        )

    def test_get_path_parameters_callable(self):
        def get_path_parameters(test_case):
            return PathParameters(ok={"id": 1})

        view_test_manager = ViewTestManager(
            simulate_request=lambda *args, **kwargs: HttpResponse(),
            path_parameters=get_path_parameters,
        )
        self.assertPathParametersEqual(
            view_test_manager.get_path_parameters(self), get_path_parameters(self)
        )

    def test_get_path_parameters_none(self):
        view_test_manager = ViewTestManager(
            simulate_request=lambda *args, **kwargs: HttpResponse(),
        )
        self.assertPathParametersEqual(
            view_test_manager.get_path_parameters(self), PathParameters(ok={})
        )

    def test_get_path_parameters_property(self):
        path_parameters = property(lambda test_case: PathParameters(ok={"id": 1}))
        view_test_manager = ViewTestManager(
            simulate_request=lambda *args, **kwargs: HttpResponse(),
            path_parameters=path_parameters,
        )
        self.assertPathParametersEqual(
            view_test_manager.get_path_parameters(self), path_parameters.fget(self)
        )

    def test_get_path_parameters_type_error(self):
        path_parameters = "string"
        # noinspection PyTypeChecker
        view_test_manager = ViewTestManager(
            simulate_request=lambda *args, **kwargs: HttpResponse(),
            path_parameters=path_parameters,
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
            simulate_request=lambda *args, **kwargs: HttpResponse(),
            query_parameters=query_parameters,
        )
        self.assertQueryParametersEqual(
            view_test_manager.get_query_parameters(self), query_parameters
        )

    def test_get_query_parameters_callable(self):
        def get_query_parameters(test_case):
            return QueryParameters(ok={"page": 1})

        view_test_manager = ViewTestManager(
            simulate_request=lambda *args, **kwargs: HttpResponse(),
            query_parameters=get_query_parameters,
        )
        self.assertQueryParametersEqual(
            view_test_manager.get_query_parameters(self), get_query_parameters(self)
        )

    def test_get_query_parameters_none(self):
        view_test_manager = ViewTestManager(
            simulate_request=lambda *args, **kwargs: HttpResponse(),
        )
        self.assertQueryParametersEqual(
            view_test_manager.get_query_parameters(self), QueryParameters(ok={})
        )

    def test_get_query_parameters_property(self):
        query_parameters = property(lambda test_case: QueryParameters(ok={"page": 1}))
        view_test_manager = ViewTestManager(
            simulate_request=lambda *args, **kwargs: HttpResponse(),
            query_parameters=query_parameters,
        )
        self.assertQueryParametersEqual(
            view_test_manager.get_query_parameters(self), query_parameters.fget(self)
        )

    def test_get_query_parameters_type_error(self):
        query_parameters = "string"
        # noinspection PyTypeChecker
        view_test_manager = ViewTestManager(
            simulate_request=lambda *args, **kwargs: HttpResponse(),
            query_parameters=query_parameters,
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
            simulate_request=lambda *args, **kwargs: HttpResponse(),
            payloads=payloads,
        )
        self.assertPayloadsEqual(view_test_manager.get_payloads(self), payloads)

    def test_get_payloads_callable(self):
        def get_payloads(test_case):
            return Payloads(ok={"name": "item 1"})

        view_test_manager = ViewTestManager(
            simulate_request=lambda *args, **kwargs: HttpResponse(),
            payloads=get_payloads,
        )
        self.assertPayloadsEqual(
            view_test_manager.get_payloads(self), get_payloads(self)
        )

    def test_get_payloads_none(self):
        view_test_manager = ViewTestManager(
            simulate_request=lambda *args, **kwargs: HttpResponse(),
        )
        self.assertPayloadsEqual(view_test_manager.get_payloads(self), Payloads(ok={}))

    def test_get_payloads_property(self):
        payloads = property(lambda test_case: Payloads(ok={"name": "item 1"}))
        view_test_manager = ViewTestManager(
            simulate_request=lambda *args, **kwargs: HttpResponse(),
            payloads=payloads,
        )
        self.assertPayloadsEqual(
            view_test_manager.get_payloads(self), payloads.fget(self)
        )

    def test_get_payloads_type_error(self):
        payloads = "string"
        # noinspection PyTypeChecker
        view_test_manager = ViewTestManager(
            simulate_request=lambda *args, **kwargs: HttpResponse(),
            payloads=payloads,
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
            simulate_request=lambda *args, **kwargs: HttpResponse(),
            headers=headers,
        )
        self.assertHeadersEqual(view_test_manager.get_headers(self), headers)

    def test_get_headers_callable(self):
        def get_headers(test_case):
            return Headers(ok={"header": "value"})

        view_test_manager = ViewTestManager(
            simulate_request=lambda *args, **kwargs: HttpResponse(),
            headers=get_headers,
        )
        self.assertHeadersEqual(view_test_manager.get_headers(self), get_headers(self))

    def test_get_headers_none(self):
        view_test_manager = ViewTestManager(
            simulate_request=lambda *args, **kwargs: HttpResponse(),
        )
        self.assertHeadersEqual(view_test_manager.get_headers(self), Headers(ok={}))

    def test_get_headers_property(self):
        headers = property(lambda test_case: Headers(ok={"header": "value"}))
        view_test_manager = ViewTestManager(
            simulate_request=lambda *args, **kwargs: HttpResponse(),
            headers=headers,
        )
        self.assertHeadersEqual(view_test_manager.get_headers(self), headers.fget(self))

    def test_get_headers_type_error(self):
        headers = "string"
        # noinspection PyTypeChecker
        view_test_manager = ViewTestManager(
            simulate_request=lambda *args, **kwargs: HttpResponse(),
            headers=headers,
        )
        with self.assertRaises(TypeError):
            view_test_manager.get_headers(self)
