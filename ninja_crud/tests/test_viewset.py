from typing import Type, Union

from django.test import TestCase

from ninja_crud.tests.test_abstract import AbstractModelViewTest
from ninja_crud.tests.test_matcher import ModelViewSetTestMatcher
from ninja_crud.views import ModelViewSet


class ModelViewSetTestMeta(type):
    def __new__(mcs, name, bases, dct):
        new_cls = super().__new__(mcs, name, bases, dct)

        if name == "ModelViewSetTest":
            return new_cls
        elif not issubclass(new_cls, TestCase):
            raise TypeError(
                f"{new_cls.__name__} must inherit from both ModelViewSetTest and django.test.TestCase"
            )  # pragma: no cover

        model_view_set_test: Union[ModelViewSetTest, TestCase] = new_cls()
        associated_model_views = []
        for attr_name in dir(new_cls):
            attr_value = getattr(new_cls, attr_name)
            if isinstance(attr_value, AbstractModelViewTest):
                attr_value.model_view_set_test = model_view_set_test
                attr_value.model_view = (
                    ModelViewSetTestMatcher.get_associated_model_view(
                        model_view_set_class=model_view_set_test.model_view_set_class,
                        test_attr_name=attr_name,
                        test_attr_value=attr_value,
                    )
                )
                associated_model_views.append(attr_value.model_view)
                for test_method_name, test_method in attr_value.get_test_methods():
                    new_test_method_name = f"{test_method_name}__{attr_name}"
                    setattr(new_cls, new_test_method_name, test_method)

        if hasattr(new_cls, "model_view_set_class"):
            ModelViewSetTestMatcher.assert_all_model_views_are_associated(
                model_view_set_class=new_cls.model_view_set_class,
                associated_model_views=associated_model_views,
            )

        return new_cls


class ModelViewSetTest(metaclass=ModelViewSetTestMeta):
    model_view_set_class: Type[ModelViewSet]
    urls_prefix: str
