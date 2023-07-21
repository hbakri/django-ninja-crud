from typing import Callable

from django.test import Client

from ninja_crud.tests.test_abstract import AbstractModelViewTest
from ninja_crud.views import CreateModelView, ListModelView, ModelViewSet


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
