import inspect
from typing import Callable, List, Tuple, Type

from django.test import Client, TestCase

from ninja_crud.views import AbstractModelView, ModelViewSet


class AbstractModelViewTest:
    model_view_set: ModelViewSet
    urls_prefix: str
    test_case: TestCase
    client: Client
    model_view_class: Type[AbstractModelView]
    name: str

    def get_test_methods(self) -> List[Tuple[str, Callable]]:
        return [
            (name, method)
            for name, method in inspect.getmembers(self, predicate=inspect.ismethod)
            if name.startswith("test")
        ]

    def get_model_view(self):
        for attr_name in dir(self.model_view_set):
            attr_value = getattr(self.model_view_set, attr_name)
            if (
                isinstance(attr_value, self.model_view_class)
                and self.name == f"test_{attr_name}"
            ):
                return attr_value
