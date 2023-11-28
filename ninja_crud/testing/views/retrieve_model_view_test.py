import http
import json
from typing import Optional

import django.http
import django.test

from ninja_crud.testing.core import ArgOrCallable, TestCaseType, ViewTestManager
from ninja_crud.testing.core.components import Headers, PathParameters
from ninja_crud.testing.views import AbstractModelViewTest
from ninja_crud.views import RetrieveModelView


class RetrieveModelViewTest(AbstractModelViewTest):
    """
    Provides a declarative and powerful way to test the retrieve model view.

    This class executes a matrix of test cases to validate the functionality of the `RetrieveModelView`,
    checking its behavior under various conditions using combinations of path parameters and headers.

    Each test method within this class is automatically attached to the test case when instantiated
    as a class attribute on a `ModelViewSetTestCase` subclass. The test method names are dynamically
    generated based on the class attribute name. For example, if the `RetrieveModelViewTest` is being
    used to test a `RetrieveModelView` named `retrieve_department_view`, the test methods will be named
    `test_retrieve_department_view__test_retrieve_model_ok`,
    `test_retrieve_department_view__test_retrieve_model_headers_unauthorized`, etc.

    This naming convention ensures clear and consistent identification of test cases.

    Attributes:
        model_view (RetrieveModelView): The retrieve model view to be tested.
        model_viewset_test_case (ModelViewSetTestCase): The test case to which this test belongs.

    Example:
    1. Let's say you defined a `RetrieveModelView` like this:
    ```python
    # examples/views/department_views.py
    from ninja_crud import views, viewsets

    from examples.models import Department
    from examples.schemas import DepartmentOut

    class DepartmentViewSet(viewsets.ModelViewSet):
        model = Department

        retrieve_department_view = views.RetrieveModelView(
            output_schema=DepartmentOut
        )
    ```
    2. You can test the `retrieve_department_view` like this:
    ```python
    # examples/tests/test_department_views.py
    from ninja_crud import testing

    from examples.views.department_views import DepartmentViewSet

    class TestDepartmentViewSet(testing.viewsets.ModelViewSetTestCase):
        model_viewset_class = DepartmentViewSet
        base_path = "api/departments"

        def setUpTestData(cls):
            super().setUpTestData()
            cls.department_1 = Department.objects.create(title="department-1")

        test_retrieve_department_view = testing.views.RetrieveModelViewTest(
            path_parameters=lambda test_case: testing.components.PathParameters(
                ok={"id": test_case.department_1.id},
                not_found={"id": 999}
            )
        )
    ```

    Note:
        The class attribute `RetrieveModelViewTest` should be named after the view being tested.
        For example, if you are testing the `retrieve_department_view` attribute of the
        `DepartmentViewSet` class, the class attribute should be named
        `test_retrieve_department_view`.
    """

    model_view: RetrieveModelView

    def __init__(
        self,
        path_parameters: ArgOrCallable[PathParameters, TestCaseType],
        headers: Optional[ArgOrCallable[Headers, TestCaseType]] = None,
    ) -> None:
        """
        Initializes the RetrieveModelViewTest with path parameters and optional headers.

        Args:
            path_parameters (ArgOrCallable[PathParameters, TestCaseType]): Path parameters for
                the request. Can be a static object, a callable, or a property on the test case.

                This can be provided in three ways:
                - As a static PathParameters object defining the path parameters.
                - As a callable (e.g., a method of ModelViewSetTestCase) that takes a 'test_case'
                    argument and returns a PathParameters object. Useful for dynamic parameter
                    generation based on test case state.
                - As a property on the ModelViewSetTestCase, dynamically providing PathParameters
                    based on the test case state.
            headers (Optional[ArgOrCallable[Headers, TestCaseType]], optional): Headers for the
                request. Similar to path_parameters, this can be a static object, a callable, or
                a property on the test case. Defaults to None.
        """
        super().__init__(model_view_class=RetrieveModelView)
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
        actual_output = json.loads(response.content)
        expected_output = self._get_expected_output(
            response=response, path_parameters=path_parameters
        )
        self.model_viewset_test_case.assertDictEqual(actual_output, expected_output)

    def _get_expected_output(
        self, response: django.http.HttpResponse, path_parameters: dict
    ) -> dict:
        model = self.model_view.retrieve_model(
            request=response.wsgi_request,  # type: ignore
            id=path_parameters["id"],
            model_class=self.model_viewset_test_case.model_viewset_class.model,
        )
        schema = self.model_view.output_schema.from_orm(model)
        return json.loads(schema.json())

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

    @django.test.tag("retrieve")
    def test_retrieve_model_ok(self):
        """
        Tests the successful scenarios.

        Executes subtests combining various `ok` path parameters and `ok` headers to verify the correct handling
        and response output under valid conditions. Each combination is tested as a subtest.
        """
        self.view_test_manager.test_view_ok(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_successful_request,
            status=http.HTTPStatus.OK,
        )

    @django.test.tag("retrieve")
    def test_retrieve_model_headers_unauthorized(self):
        """
        Tests the unauthorized headers scenarios.

        Executes subtests combining various `ok` path parameters and `unauthorized` headers to verify the correct
        handling and response output under unauthorized conditions. Each combination of parameters is tested.
        """
        self.view_test_manager.test_view_headers_unauthorized(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )

    @django.test.tag("retrieve")
    def test_retrieve_model_headers_forbidden(self):
        """
        Tests the forbidden headers scenarios.

        Executes subtests combining various `ok` path parameters and `forbidden` headers to verify the correct
        handling and response output under forbidden conditions. Each combination of parameters is tested.
        """
        self.view_test_manager.test_view_headers_forbidden(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )

    @django.test.tag("retrieve")
    def test_retrieve_model_path_parameters_not_found(self):
        """
        Tests the not found path parameter scenarios.

        Executes subtests combining various `not_found` path parameters and `ok` headers to verify the correct
        handling and response output under not found conditions. Each combination of parameters is tested.
        """
        self.view_test_manager.test_view_path_parameters_not_found(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )
