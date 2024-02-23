import http
import json
import logging
from typing import Optional, get_args

import django.db.models
import django.http
import django.test
import ninja.pagination

from ninja_crud.testing.core import ArgOrCallable, TestCaseType, ViewTestManager
from ninja_crud.testing.core.components import Headers, PathParameters, QueryParameters
from ninja_crud.testing.views import AbstractModelViewTest
from ninja_crud.views import ListModelView

logger = logging.getLogger(__name__)


class ListModelViewTest(AbstractModelViewTest):
    """
    Provides a declarative and powerful way to test the list model view.

    This class executes a matrix of test cases to validate the functionality of the `ListModelView`,
    assessing its behavior under various conditions using combinations of path parameters, headers,
    and query parameters.

    Each test method within this class is automatically attached to the test case when instantiated
    as a class attribute on a `ModelViewSetTestCase` subclass. The test method names are dynamically
    generated based on the class attribute name. For example, if the `ListModelViewTest` is used
    to test a `ListModelView` named `list_departments_view`, the test methods will be named
    `test_list_departments_view__test_list_models_ok`,
    `test_list_departments_view__test_list_models_headers_unauthorized`, etc.

    This naming convention ensures clear and consistent identification of test cases.

    Attributes:
        model_view (ListModelView): The list model view to be tested.
        model_viewset_test_case (ModelViewSetTestCase): The test case to which this test belongs.

    Example:
    1. Let's say you defined a `ListModelView` like this:
    ```python
    # examples/views/department_views.py
    from ninja_crud import views, viewsets

    from examples.models import Department
    from examples.schemas import DepartmentOut

    class DepartmentViewSet(viewsets.ModelViewSet):
        model = Department

        list_departments_view = views.ListModelView(
            response_body=DepartmentOut
        )
    ```
    2. You can test the `list_departments_view` like this:
    ```python
    # examples/tests/test_department_views.py
    from ninja_crud import testing

    from examples.views.department_views import DepartmentViewSet

    class TestDepartmentViewSet(testing.viewsets.ModelViewSetTestCase):
        model_viewset_class = DepartmentViewSet
        base_path = "api/departments"

        def setUpTestData(cls):
            cls.department_1 = Department.objects.create(title="department-1")
            cls.department_2 = Department.objects.create(title="department-2")
            cls.department_3 = Department.objects.create(title="department-3")

        test_list_departments_view = testing.views.ListModelViewTest(
            query_parameters=testing.components.QueryParameters(
                ok={"limit": 10, "offset": 0},
                bad_request={"limit": -1, "offset": -1}
            )
        )
    ```

    Note:
        The class attribute `ListModelViewTest` should be named after the view being tested.
        For example, if you are testing the `list_departments_view` attribute of the
        `DepartmentViewSet` class, the class attribute should be named
        `test_list_departments_view`.
    """

    model_view: ListModelView

    def __init__(
        self,
        path_parameters: Optional[ArgOrCallable[PathParameters, TestCaseType]] = None,
        query_parameters: Optional[ArgOrCallable[QueryParameters, TestCaseType]] = None,
        headers: Optional[ArgOrCallable[Headers, TestCaseType]] = None,
    ) -> None:
        """
        Initializes the ListModelViewTest with path parameters, query parameters, and optional headers.

        Args:
            path_parameters (Optional[ArgOrCallable[PathParameters, TestCaseType]], optional): Path parameters for
                the request. Can be a static object, a callable, or a property on the test case. Defaults to None.
            query_parameters (Optional[ArgOrCallable[QueryParameters, TestCaseType]], optional): Query parameters for
                the request. Can be a static object, a callable, or a property on the test case. Defaults to None.
            headers (Optional[ArgOrCallable[Headers, TestCaseType]], optional): Headers for the
                request. Can be a static object, a callable, or a property on the test case. Defaults to None.
        """
        super().__init__(model_view_class=ListModelView)
        self.view_test_manager = ViewTestManager(
            simulate_request=self.simulate_request,
            path_parameters=path_parameters,
            query_parameters=query_parameters,
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
        """
        Callback method to handle the response for a successful request.

        This method is called when the view returns a successful HTTP response. It verifies that
        the response content matches the expected output, ensuring the correctness of the view's output.
        The expected output is derived from the model instance specified in the path parameters.

        Args:
            response (django.http.HttpResponse): The HttpResponse object from the view.
            path_parameters (dict): The path parameters used in the request.
            query_parameters (dict): The query parameters used in the request.
            headers (dict): The headers used in the request.
            payload (dict): The payload sent with the request.
        """
        content = json.loads(response.content)
        queryset = self._get_queryset(
            response=response,
            path_parameters=path_parameters,
            query_parameters=query_parameters,
        )

        if self.model_view.pagination_class is None:
            self.model_viewset_test_case.assertIsInstance(content, list)
            self.model_viewset_test_case.assertEqual(len(content), queryset.count())
            self._validate_response_items(items=content, queryset=queryset)

        elif self.model_view.pagination_class == ninja.pagination.LimitOffsetPagination:
            self.model_viewset_test_case.assertIsInstance(content, dict)
            self.model_viewset_test_case.assertIn("count", content)
            self.model_viewset_test_case.assertIsInstance(content["count"], int)
            self.model_viewset_test_case.assertEqual(
                content["count"],
                queryset.count(),
            )

            limit = query_parameters.get("limit", 100)
            offset = query_parameters.get("offset", 0)
            self.model_viewset_test_case.assertIn("items", content)
            self.model_viewset_test_case.assertIsInstance(content["items"], list)
            self.model_viewset_test_case.assertEqual(
                len(content["items"]),
                queryset[offset : offset + limit].count(),  # noqa: E203
            )
            self._validate_response_items(items=content["items"], queryset=queryset)

        else:  # pragma: no cover
            logger.warning(
                f"Unsupported pagination class: {self.model_view.pagination_class}"
            )

    def _get_queryset(
        self,
        response: django.http.HttpResponse,
        path_parameters: dict,
        query_parameters: dict,
    ) -> django.db.models.QuerySet:
        path_parameters = (
            self.model_view.path_parameters(**path_parameters)
            if self.model_view.path_parameters
            else None
        )
        query_parameters = (
            self.model_view.query_parameters(**query_parameters)
            if self.model_view.query_parameters
            else None
        )
        return self.model_view.handle_request(
            request=getattr(response, "wsgi_request", None),
            path_parameters=path_parameters,
            query_parameters=query_parameters,
            request_body=None,
        )

    def _validate_response_items(
        self, items: list, queryset: django.db.models.QuerySet
    ):
        for item in items:
            self.model_viewset_test_case.assertIsInstance(item, dict)
            model = queryset.get(id=item["id"])
            response_body_class = get_args(self.model_view.response_body)[0]
            response_body = response_body_class.from_orm(model)
            self.model_viewset_test_case.assertDictEqual(
                item, json.loads(response_body.json())
            )

    def on_failed_request(
        self,
        response: django.http.HttpResponse,
        path_parameters: dict,
        query_parameters: dict,
        headers: dict,
        payload: dict,
    ):
        """
        Callback method to handle the response for a failed request.

        This method is called when the view returns a failed HTTP response. It only verifies that
        the response status code matches the expected status code, ensuring the correctness of the
        view's error handling.

        Args:
            response (django.http.HttpResponse): The HttpResponse object from the view.
            path_parameters (dict): The path parameters used in the request.
            query_parameters (dict): The query parameters used in the request.
            headers (dict): The headers used in the request.
            payload (dict): The payload sent with the request.
        """
        pass

    @django.test.tag("list")
    def test_list_models_ok(self):
        """
        Tests the successful scenarios.

        Executes subtests combining various `ok` path parameters, `ok` query parameters, and `ok` headers to verify
        the correct handling and response output under valid conditions. Each combination is tested as a subtest.
        """
        self.view_test_manager.test_view_ok(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_successful_request,
            status=http.HTTPStatus.OK,
        )

    @django.test.tag("list")
    def test_list_models_query_parameters_bad_request(self):
        """
        Tests the bad request query parameter scenarios.

        Executes subtests combining various `ok` path parameters, `bad_request` query parameters, and `ok` headers to
        verify the correct handling and response output under bad request conditions. Each combination of
        parameters is tested.
        """
        self.view_test_manager.test_view_query_parameters_bad_request(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )

    @django.test.tag("list")
    def test_list_models_headers_unauthorized(self):
        """
        Tests the unauthorized headers scenarios.

        Executes subtests combining various `ok` path parameters, `ok` query parameters, and `unauthorized` headers to
        verify the correct handling and response output under unauthorized conditions. Each combination of
        parameters is tested.
        """
        self.view_test_manager.test_view_headers_unauthorized(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )

    @django.test.tag("list")
    def test_list_models_headers_forbidden(self):
        """
        Tests the forbidden headers scenarios.

        Executes subtests combining various `ok` path parameters, `ok` query parameters, and `forbidden` headers to
        verify the correct handling and response output under forbidden conditions. Each combination of
        parameters is tested.
        """
        self.view_test_manager.test_view_headers_forbidden(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )

    @django.test.tag("list")
    def test_list_models_path_parameters_not_found(self):
        """
        Tests the not found path parameter scenarios.

        Executes subtests combining various `not_found` path parameters, `ok` query parameters, and `ok` headers to
        verify the correct handling and response output under not found conditions. Each combination of
        parameters is tested.
        """
        self.view_test_manager.test_view_path_parameters_not_found(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )
