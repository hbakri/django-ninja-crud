import http
import json
from typing import Optional

import django.http
import django.test

from ninja_crud.testing.core import ArgOrCallable, TestCaseType, ViewTestManager
from ninja_crud.testing.core.components import Headers, PathParameters, Payloads
from ninja_crud.testing.views import AbstractModelViewTest
from ninja_crud.views import UpdateModelView


class UpdateModelViewTest(AbstractModelViewTest):
    """
    Provides a declarative and powerful way to test the update model view.

    This class executes a matrix of test cases to validate the functionality of the `UpdateModelView`,
    assessing its behavior under various conditions using combinations of path parameters, headers,
    and payloads.

    Each test method within this class is automatically attached to the test case when instantiated
    as a class attribute on a `ModelViewSetTestCase` subclass. The test method names are dynamically
    generated based on the class attribute name. For example, if the `UpdateModelViewTest` is used
    to test an `UpdateModelView` named `update_department_view`, the test methods will be named
    `test_update_department_view__test_update_model_ok`,
    `test_update_department_view__test_update_model_headers_unauthorized`, etc.

    This naming convention ensures clear and consistent identification of test cases.

    Attributes:
        model_view (UpdateModelView): The update model view to be tested.
        model_viewset_test_case (ModelViewSetTestCase): The test case to which this test belongs.

    Example:
    1. Let's say you defined an `UpdateModelView` like this:
    ```python
    # examples/views/department_views.py
    from ninja_crud import views, viewsets

    from examples.models import Department
    from examples.schemas import DepartmentIn, DepartmentOut

    class DepartmentViewSet(viewsets.ModelViewSet):
        model = Department

        update_department_view = views.UpdateModelView(
            input_schema=DepartmentIn,
            output_schema=DepartmentOut
        )
    ```
    2. You can test the `update_department_view` like this:
    ```python
    # examples/tests/test_department_views.py
    from ninja_crud import testing

    from examples.views.department_views import DepartmentViewSet

    class TestDepartmentViewSet(testing.viewsets.ModelViewSetTestCase):
        model_viewset_class = DepartmentViewSet
        base_path = "api/departments"

        def setUpTestData(cls):
            super().setUpTestData()
            cls.department = Department.objects.create(title="department")

        test_update_department_view = testing.views.UpdateModelViewTest(
            path_parameters=testing.components.PathParameters(
                ok={"id": 1},
                not_found={"id": 999}
            ),
            payloads=testing.components.Payloads(
                ok={"title": "updated department"},
                bad_request={"title": ""}
            )
        )
    ```

    Note:
        The class attribute `UpdateModelViewTest` should be named after the view being tested.
        For example, if you are testing the `update_department_view` attribute of the
        `DepartmentViewSet` class, the class attribute should be named
        `test_update_department_view`.
    """

    model_view: UpdateModelView

    def __init__(
        self,
        path_parameters: ArgOrCallable[PathParameters, TestCaseType],
        payloads: ArgOrCallable[Payloads, TestCaseType],
        headers: Optional[ArgOrCallable[Headers, TestCaseType]] = None,
    ) -> None:
        super().__init__(model_view_class=UpdateModelView)
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
    ) -> None:
        model = self.model_viewset_test_case.model_viewset_class.model.objects.get(
            id=path_parameters["id"]
        )
        schema = self.model_view.output_schema.from_orm(model)

        content = json.loads(response.content)
        self.model_viewset_test_case.assertDictEqual(content, json.loads(schema.json()))

    def on_failed_request(
        self,
        response: django.http.HttpResponse,
        path_parameters: dict,
        query_parameters: dict,
        headers: dict,
        payload: dict,
    ) -> None:
        pass

    @django.test.tag("update")
    def test_update_model_ok(self):
        self.view_test_manager.test_view_ok(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_successful_request,
            status=http.HTTPStatus.OK,
        )

    @django.test.tag("update")
    def test_update_model_bad_request(self):
        self.view_test_manager.test_view_payloads_bad_request(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )

    @django.test.tag("update")
    def test_update_model_conflict(self):
        self.view_test_manager.test_view_payloads_conflict(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )

    @django.test.tag("update")
    def test_update_model_unauthorized(self):
        self.view_test_manager.test_view_headers_unauthorized(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )

    @django.test.tag("update")
    def test_update_model_forbidden(self):
        self.view_test_manager.test_view_headers_forbidden(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )

    @django.test.tag("update")
    def test_update_model_not_found(self):
        self.view_test_manager.test_view_path_parameters_not_found(
            test_case=self.model_viewset_test_case,
            on_completion=self.on_failed_request,
        )
