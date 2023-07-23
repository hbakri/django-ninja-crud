import inspect
from typing import TYPE_CHECKING, Callable, List, Tuple, Type, Union

from django.test import TestCase

from ninja_crud.views import AbstractModelView

if TYPE_CHECKING:  # pragma: no cover
    from ninja_crud.tests.test_viewset import ModelViewSetTest


class AbstractModelViewTest:
    model_view_class: Type[AbstractModelView]
    model_view: AbstractModelView

    model_view_set_test: Union["ModelViewSetTest", TestCase]

    def get_test_methods(self) -> List[Tuple[str, Callable]]:
        return [
            (name, method)
            for name, method in inspect.getmembers(self, predicate=inspect.ismethod)
            if name.startswith("test")
        ]
