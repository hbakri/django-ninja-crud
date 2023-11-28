import http
import json
from typing import Optional

import django.http
import django.test

from ninja_crud.testing.core import ArgOrCallable, TestCaseType, ViewTestManager
from ninja_crud.testing.core.components import Headers, PathParameters, Payloads
from ninja_crud.testing.views import AbstractModelViewTest
from ninja_crud.views import CreateModelView


class CreateModelViewTest(AbstractModelViewTest):
    """
    Provides a declarative and powerful way to test the create model view.

    This class executes a matrix of test cases to validate the functionality of the `CreateModelView`,
    assessing its behavior under various conditions using combinations of path parameters, headers,
    and payloads.

    Each test method within this class is automatically attached to the test case when instantiated
    as a class attribute on a `ModelViewSetTestCase` subclass. The test method names are dynamically
    generated based on the class attribute name. For example, if the `CreateModelViewTest` is used
    to test a `CreateModelView` named `create_department_view`, the test methods will be named
    `test_create_department_view__test_create_model_ok`,
    `test_create_department_view__test_create_model_headers_unauthorized`, etc.

    This naming convention ensures clear and consistent identification of test cases.

    Attributes:
        model_view (CreateModelView): The create model view to be tested.
        model_viewset_test_case (ModelViewSetTestCase): The test case to which this test belongs.

    Example:
    1. Let's say you defined a `CreateModelView` like this:
    ```python
    # examples/views/department_views.py
    from ninja_crud import views, viewsets

    from examples.models import Department
    from examples.schemas import DepartmentIn, DepartmentOut

    class DepartmentViewSet(viewsets.ModelViewSet):
        model = Department

        create_department_view = views.CreateModelView(
            input_schema=DepartmentIn,
            output_schema=DepartmentOut
        )
    ```
    2. You can test the `create_department_view` like this:
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

        test_create_department_view = testing.views.CreateModelViewTest(
            payloads=lambda test_case: testing.components.Payloads(
                ok={"title": "department"},
                bad_request={"title": ""},
                conflict={"title": test_case.department_1.title}
            )
        )
    ```

    Note:
        The class attribute `CreateModelViewTest` should be named after the view being tested.
        For example, if you are testing the `create_department_view` attribute of the
        `DepartmentViewSet` class, the class attribute should be named
        `test_create_department_view`.
    """

    model_view: CreateModelView

    def __init__(
        self,
        payloads: ArgOrCallable[Payloads, TestCaseType],
        path_parameters: Optional[ArgOrCallable[PathParameters, TestCaseType]] = None,
        headers: Optional[ArgOrCallable[Headers, TestCaseType]] = None,
    ) -> None:
        """
        Initializes the CreateModelViewTest with payloads, optional path parameters, and optional headers.

        Args:
            payloads (ArgOrCallable[Payloads, TestCaseType]): Payloads for the request. Can be a
                static object, a callable, or a property on the test case.
            path_parameters (Optional[ArgOrCallable[PathParameters, TestCaseType]], optional): Path parameters for
                the request. Can be a static object, a callable, or a property on the test case. Defaults to None.
            headers (Optional[ArgOrCallable[Headers, TestCaseType]], optional): Headers for the
                request. Can be a static object, a callable, or a property on the test case. Defaults to None.
        """
        super().__init__(model_view_class=CreateModelView)
        self.view_test_manager = ViewTestManager(
            handle_request=self.handle_request,
            path_parameters=path_parameters,
            headers=headers,
            payloads=payloads,
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
        self.model_viewset_test_case.assertIsInstance(content, dict)
        self.model_viewset_test_case.assertIn("id", content)

        if self.model_view.detail:
            model_class = self.model_view._related_model_class
        else:
            model_class = self.model_viewset_test_case.model_viewset_class.model
        model = model_class.objects.get(id=content["id"])
        schema = self.model_view.output_schema.from_orm(model)
        self.model_viewset_test_case.assertDictEqual(content, json.loads(schema.json()))

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

    @django.test.tag("create")
    def test_create_model_ok(self):
        """
        Tests the successful scenarios.

        Executes subtests combining various `ok` payloads, `ok` path parameters, and `ok` headers to verify
        the correct handling and response output under valid conditions. Each combination is tested as a subtest.
        """
        self.view_test_manager.test_view_ok(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_successful_request,
            status=http.HTTPStatus.CREATED,
        )

    @django.test.tag("create")
    def test_create_model_payloads_bad_request(self):
        """
        Tests the bad request payload scenarios.

        Executes subtests combining various `ok` path parameters, `bad_request` payloads, and `ok` headers to
        verify the correct handling and response output under bad request conditions. Each combination of
        parameters is tested.
        """
        self.view_test_manager.test_view_payloads_bad_request(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )

    @django.test.tag("create")
    def test_create_model_payloads_conflict(self):
        """
        Tests the conflict payload scenarios.

        Executes subtests combining various `ok` path parameters, `conflict` payloads, and `ok` headers to
        verify the correct handling and response output under conflict conditions. Each combination of
        parameters is tested.
        """
        self.view_test_manager.test_view_payloads_conflict(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )

    @django.test.tag("create")
    def test_create_model_headers_unauthorized(self):
        """
        Tests the unauthorized headers scenarios.

        Executes subtests combining various `ok` path parameters, `ok` payloads, and `unauthorized` headers to
        verify the correct handling and response output under unauthorized conditions. Each combination of
        parameters is tested.
        """
        self.view_test_manager.test_view_headers_unauthorized(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )

    @django.test.tag("create")
    def test_create_model_headers_forbidden(self):
        """
        Tests the forbidden headers scenarios.

        Executes subtests combining various `ok` path parameters, `ok` payloads, and `forbidden` headers to
        verify the correct handling and response output under forbidden conditions. Each combination of
        parameters is tested.
        """
        self.view_test_manager.test_view_headers_forbidden(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )

    @django.test.tag("create")
    def test_create_model_path_parameters_not_found(self):
        """
        Tests the not found path parameter scenarios.

        Executes subtests combining various `not_found` path parameters, `ok` payloads, and `ok` headers to
        verify the correct handling and response output under not found conditions. Each combination of
        parameters is tested.
        """
        self.view_test_manager.test_view_path_parameters_not_found(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )
