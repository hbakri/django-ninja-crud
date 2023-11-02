from typing import TYPE_CHECKING, Type

from ninja_crud.views import AbstractModelView

if TYPE_CHECKING:  # pragma: no cover
    from ninja_crud.testing.viewsets import ModelViewSetTestCase


class AbstractModelViewTest:
    test_model_view_set: "ModelViewSetTestCase"
    model_view: AbstractModelView

    def __init__(self, model_view_class: Type[AbstractModelView]) -> None:
        self.model_view_class = model_view_class

    def bind_to_test_viewset(self, test_viewset: "ModelViewSetTestCase") -> None:
        self.test_model_view_set = test_viewset

    def bind_to_view(self, view: AbstractModelView) -> None:
        self.model_view = view
