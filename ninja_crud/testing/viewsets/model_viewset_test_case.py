import inspect
import logging
from typing import List, Type

import django.test

from ninja_crud.testing.views import AbstractModelViewTest
from ninja_crud.views import AbstractModelView
from ninja_crud.viewsets import ModelViewSet

logger = logging.getLogger(__name__)


class ModelViewSetTestCase(django.test.TestCase):
    """
    A base class for testing `ModelViewSet` subclasses in Django.

    Provides automated validation, binding, and test method registration for subclasses,
    ensuring comprehensive and consistent testing of `ModelViewSet` instances.

    Attributes:
        model_viewset_class (Type[ModelViewSet]): The ModelViewSet subclass to test.
        base_path (str): The base path for the model views.

    Example:
    1. Define your `ModelViewSet` and register its routes:
    ```python
    # examples/views/department_views.py
    from ninja import Router
    from ninja_crud import views, viewsets

    from examples.models import Department
    from examples.schemas import DepartmentIn, DepartmentOut

    router = Router()

    class DepartmentViewSet(viewsets.ModelViewSet):
        model = Department
        default_request_body = DepartmentIn
        default_response_body = DepartmentOut

        list_departments = views.ListModelView()
        create_department = views.CreateModelView()
        retrieve_department = views.RetrieveModelView()
        update_department = views.UpdateModelView()
        delete_department = views.DeleteModelView()

    DepartmentViewSet.register_routes(router)
    ```

    2. Include your router in your Ninja API configuration:
    ```python
    # config/api.py
    from ninja import NinjaAPI
    from examples.views.department_views import router as department_router

    api = NinjaAPI(urls_namespace="api")
    api.add_router("departments", department_router)
    ```

    3. Create your test class by subclassing `ModelViewSetTestCase`:
    ```python
    # examples/tests/test_department_views.py
    from ninja_crud import testing

    from examples.models import Department
    from examples.views.department_views import DepartmentViewSet

    class TestDepartmentViewSet(testing.viewsets.ModelViewSetTestCase):
        model_viewset_class = DepartmentViewSet
        base_path = "api/departments"

        @classmethod
        def setUpTestData(cls):
            cls.department_1 = Department.objects.create(title="department-1")
            cls.department_2 = Department.objects.create(title="department-2")

        @property
        def path_parameters(self):
            return testing.components.PathParameters(
                ok={"id": self.department_1.id},
                not_found={"id": 9999}
            )

        @property
        def payloads(self):
            return testing.components.Payloads(
                ok={"title": "department-3"},
                bad_request={},
                conflict={"title": self.department_2.title},
            )

        test_list_departments = testing.views.ListModelViewTest()
        test_create_department = testing.views.CreateModelViewTest(payloads)
        test_retrieve_department = testing.views.RetrieveModelViewTest(path_parameters)
        test_update_department = testing.views.UpdateModelViewTest(path_parameters, payloads)
        test_delete_department = testing.views.DeleteModelViewTest(path_parameters)
    ```

    Note:
        This class should not be instantiated directly. Instead, it should be subclassed.
        It utilizes the `__init_subclass__` method to perform automatic validation,
        binding of `AbstractModelViewTest` instances, and registration of test methods.
    """

    model_viewset_class: Type[ModelViewSet]
    base_path: str

    def __init_subclass__(cls, **kwargs):
        """
        Special method in Python that is automatically called when a class is subclassed.

        For `ModelViewSetTestCase` subclasses, this method is used to validate the class
        attributes, bind the `AbstractModelViewTest` instances to the subclass and to
        their corresponding model views, and register the test methods. It should not be
        called directly.
        """
        super().__init_subclass__(**kwargs)

        if hasattr(cls, "model_viewset_class"):
            cls._bind_test_model_views()
            cls._register_test_methods()

    @classmethod
    def _bind_test_model_views(cls):
        """
        Binds instances of `AbstractModelViewTest` to their corresponding model views.

        This method creates an instance of `ModelViewSetTestCase` and uses it to bind each
        `AbstractModelViewTest` instance to the `ModelViewSetTestCase` subclass and to the
        corresponding model view in the `ModelViewSet`. It also checks that all model views
        in the `ModelViewSet` are associated with a test.

        Note:
            This method is called automatically during the subclass initialization of
            `ModelViewSetTestCase` and should not be called directly.
        """
        associated_model_views = []
        cls_instance = cls()
        for attr_name, attr_value in inspect.getmembers(cls):
            if attr_name.startswith("test") and isinstance(
                attr_value, AbstractModelViewTest
            ):
                test_model_view_name, test_model_view = attr_name, attr_value
                test_model_view.bind_to_model_viewset_test_case(
                    model_viewset_test_case=cls_instance
                )
                associated_model_view = cls._get_associated_model_view(
                    test_attr_name=test_model_view_name,
                    model_view_class=test_model_view.model_view_class,
                )
                test_model_view.bind_to_model_view(model_view=associated_model_view)
                associated_model_views.append(associated_model_view)

        cls._check_all_model_views_associated(
            associated_model_views=associated_model_views
        )

    @classmethod
    def _register_test_methods(cls):
        """
        Registers test methods from `AbstractModelViewTest` instances as class methods.

        Iterates over all attributes of the class, finds `AbstractModelViewTest` instances
        with names starting with "test", and registers their test methods (methods starting
        with "test") as class methods on the `ModelViewSetTestCase` subclass.

        The registered test methods follow the naming convention:
        `<name of AbstractModelViewTest instance>__<name of test method>`

        Note:
            This method is called automatically during the subclass initialization of
            `ModelViewSetTestCase` and should not be called directly.
        """
        for attr_name, attr_value in inspect.getmembers(cls):
            if attr_name.startswith("test") and isinstance(
                attr_value, AbstractModelViewTest
            ):
                for method_name, method in inspect.getmembers(
                    attr_value, predicate=inspect.ismethod
                ):
                    if method_name.startswith("test"):
                        new_test_method_name = f"{attr_name}__{method_name}"
                        setattr(cls, new_test_method_name, method)

    @classmethod
    def _get_associated_model_view(
        cls, test_attr_name: str, model_view_class: Type[AbstractModelView]
    ) -> AbstractModelView:
        """
        Finds the model view associated with a `AbstractModelViewTest` instance.

        This method relies on a naming convention where the `AbstractModelViewTest` instance
        must be named as "test_<name of model view>". It raises a `ValueError` if the associated
        model view cannot be found.

        Parameters:
            - test_attr_name (str): The name of the `AbstractModelViewTest` attribute.
            - model_view_class (Type[AbstractModelView]): The class of the model view to find.

        Returns:
            - AbstractModelView: The model view associated with the `AbstractModelViewTest` instance.

        Raises:
            - ValueError: If the associated model view cannot be found.
        """
        for attr_name, attr_value in inspect.getmembers(cls.model_viewset_class):
            if (
                isinstance(attr_value, model_view_class)
                and test_attr_name == f"test_{attr_name}"
            ):
                return attr_value
        raise ValueError(
            f"Could not find associated model view for '{cls.__name__}.{test_attr_name}'"
        )

    @classmethod
    def _check_all_model_views_associated(
        cls, associated_model_views: List[AbstractModelView]
    ) -> None:
        """
        Checks that all model views in the `ModelViewSet` are associated with a test.

        Iterates over all model views in the `ModelViewSet`, and logs a warning for any
        model view that is not associated with a test.

        Parameters:
            - associated_model_views (List[AbstractModelView]): A list of all model views
                that have been associated with a test.
        """
        for attr_name, attr_value in inspect.getmembers(cls.model_viewset_class):
            if (
                isinstance(attr_value, AbstractModelView)
                and attr_value not in associated_model_views
            ):
                logger.warning(
                    f"Model view '{cls.model_viewset_class.__name__}.{attr_name}' is not associated with any test"
                )
