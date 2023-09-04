from __future__ import annotations

import logging
from typing import Type, Union

from django.test import TestCase

from ninja_crud.tests.test_abstract import AbstractModelViewTest
from ninja_crud.tests.test_matcher import ModelViewSetTestMatcher
from ninja_crud.views import ModelViewSet

logger = logging.getLogger(__name__)


class ModelViewSetTestMeta(type):
    @staticmethod
    def validate_model_view_set_class(
        new_cls: ModelViewSetTestMeta,
    ):  # pragma: no cover
        cls_attr_name = "model_view_set_class"
        if not hasattr(new_cls, cls_attr_name):
            raise ValueError(
                f"{new_cls.__name__}.{cls_attr_name} class attribute must be set"
            )
        cls_attr_value = getattr(new_cls, cls_attr_name)
        if not isinstance(cls_attr_value, type) or not issubclass(
            cls_attr_value, ModelViewSet
        ):
            raise ValueError(
                f"{new_cls.__name__}.{cls_attr_name} must be a subclass of ModelViewSet"
            )

    @staticmethod
    def validate_base_path(new_cls: ModelViewSetTestMeta):  # pragma: no cover
        cls_attr_name = "base_path"
        if not hasattr(new_cls, cls_attr_name):
            raise ValueError(
                f"{new_cls.__name__}.{cls_attr_name} class attribute must be set"
            )
        cls_attr_value = getattr(new_cls, cls_attr_name)
        if not isinstance(cls_attr_value, str):
            raise ValueError(
                f"{new_cls.__name__}.{cls_attr_name} must be a string, not {type(cls_attr_value).__name__}"
            )

    def __new__(mcs, name, bases, dct):
        new_cls = super().__new__(mcs, name, bases, dct)

        if name in ("ModelViewSetTest", "TestModelViewSet"):
            return new_cls
        elif not issubclass(new_cls, TestCase):
            raise TypeError(
                f"{new_cls.__name__} must inherit from both ModelViewSetTest and django.test.TestCase"
            )  # pragma: no cover

        mcs.validate_model_view_set_class(new_cls)
        mcs.validate_base_path(new_cls)

        test_model_view_set: Union[TestModelViewSet, TestCase] = new_cls()
        associated_model_views = []
        for attr_name in dir(new_cls):
            attr_value = getattr(new_cls, attr_name)
            if isinstance(attr_value, AbstractModelViewTest):
                attr_value.test_model_view_set = test_model_view_set
                attr_value.model_view = (
                    ModelViewSetTestMatcher.get_associated_model_view(
                        model_view_set_class=test_model_view_set.model_view_set_class,
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


class TestModelViewSet(metaclass=ModelViewSetTestMeta):
    model_view_set_class: Type[ModelViewSet]
    base_path: str


class ModelViewSetTest(TestModelViewSet):
    def __init__(self, *args, **kwargs):  # pragma: no cover
        logger.warning(
            f"{ModelViewSetTest.__name__} is deprecated, use {TestModelViewSet.__name__} instead",
            DeprecationWarning,
        )
        super().__init__(*args, **kwargs)
