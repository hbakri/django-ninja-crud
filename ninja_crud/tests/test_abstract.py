import inspect
from typing import Callable, List, Tuple, Type

from django.test import Client, TestCase

from ninja_crud.views import (
    AbstractModelView,
    CreateModelView,
    ListModelView,
    ModelViewSet,
)


class AbstractModelViewTest:
    model_view_set: ModelViewSet
    urls_prefix: str
    test_case: TestCase
    client: Client
    model_view: Type[AbstractModelView]
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
                isinstance(attr_value, self.model_view)
                and self.name == f"test_{attr_name}"
            ):
                return attr_value


class ModelViewSetTestMeta(type):
    model_view_set_class: ModelViewSet
    urls_prefix: str
    client_class: Callable[[], Client]

    def __new__(mcs, name, bases, dct):
        new_cls = super().__new__(mcs, name, bases, dct)
        test_case = new_cls()
        for attr_name in dir(new_cls):
            attr_value = getattr(new_cls, attr_name)
            if isinstance(attr_value, AbstractModelViewTest):
                attr_value.model_view_set = new_cls.model_view_set_class
                attr_value.urls_prefix = new_cls.urls_prefix
                attr_value.test_case = test_case
                attr_value.client = new_cls.client_class()
                attr_value.name = attr_name
                for test_name, test_func in attr_value.get_test_methods():
                    model_view = attr_value.get_model_view()
                    model_name = new_cls.model_view_set_class.model.__name__.lower()
                    substring_replace = model_name
                    if (
                        isinstance(model_view, (ListModelView, CreateModelView))
                        and model_view.detail
                    ):
                        related_model_name = model_view.related_model.__name__.lower()
                        substring_replace = f"{model_name}_{related_model_name}"
                    new_test_name = test_name.replace("model", substring_replace)
                    setattr(new_cls, new_test_name, test_func)
        return new_cls


class ModelViewSetTest(metaclass=ModelViewSetTestMeta):
    model_view_set_class: ModelViewSet
    urls_prefix: str
