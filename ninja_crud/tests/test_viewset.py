from typing import Type

from ninja_crud.tests.test_abstract import AbstractModelViewTest
from ninja_crud.tests.test_matcher import ModelViewSetTestMatcher
from ninja_crud.views import CreateModelView, ListModelView, ModelViewSet


class ModelViewSetTestMeta(type):
    model_view_set_class: Type[ModelViewSet]
    urls_prefix: str

    def __new__(mcs, name, bases, dct):
        new_cls = super().__new__(mcs, name, bases, dct)
        test_case = new_cls()
        associated_model_views = []
        for attr_name in dir(new_cls):
            attr_value = getattr(new_cls, attr_name)
            if isinstance(attr_value, AbstractModelViewTest):
                attr_value.model_view_set_class = new_cls.model_view_set_class
                attr_value.urls_prefix = new_cls.urls_prefix
                attr_value.test_case = test_case
                attr_value.model_view = (
                    ModelViewSetTestMatcher.get_associated_model_view(
                        model_view_set_class=new_cls.model_view_set_class,
                        test_attr_name=attr_name,
                        test_attr_value=attr_value,
                    )
                )
                associated_model_views.append(attr_value.model_view)
                for test_name, test_func in attr_value.get_test_methods():
                    model_name = new_cls.model_view_set_class.model_class.__name__.lower()
                    substring_replace = model_name
                    if (
                        isinstance(
                            attr_value.model_view, (ListModelView, CreateModelView)
                        )
                        and attr_value.model_view.detail
                    ):
                        related_model_name = (
                            attr_value.model_view.related_model.__name__.lower()
                        )
                        substring_replace = f"{model_name}_{related_model_name}"
                    new_test_name = test_name.replace("model", substring_replace)
                    setattr(new_cls, new_test_name, test_func)

        if hasattr(new_cls, "model_view_set_class"):
            ModelViewSetTestMatcher.assert_all_model_views_are_associated(
                model_view_set_class=new_cls.model_view_set_class,
                associated_model_views=associated_model_views,
            )

        return new_cls


class ModelViewSetTest(metaclass=ModelViewSetTestMeta):
    model_view_set_class: Type[ModelViewSet]
    urls_prefix: str
