import inspect
from typing import Callable, List, Tuple, Type

from django.test import TestCase

from ninja_crud.views import AbstractModelView, ModelViewSet


class AbstractModelViewTest:
    model_view_class: Type[AbstractModelView]
    model_view: AbstractModelView

    model_view_set_class: Type[ModelViewSet]
    urls_prefix: str
    test_case: TestCase

    def get_test_methods(self) -> List[Tuple[str, Callable]]:
        return [
            (name, method)
            for name, method in inspect.getmembers(self, predicate=inspect.ismethod)
            if name.startswith("test")
        ]
