from typing import TYPE_CHECKING, Type

from ninja_crud.views import AbstractModelView

if TYPE_CHECKING:  # pragma: no cover
    from ninja_crud.testing.viewsets import ModelViewSetTestCase


class AbstractModelViewTest:
    model_viewset_test_case: "ModelViewSetTestCase"
    model_view: AbstractModelView

    def __init__(self, model_view_class: Type[AbstractModelView]) -> None:
        self.model_view_class = model_view_class

    def bind_to_model_viewset_test_case(
        self, model_viewset_test_case: "ModelViewSetTestCase"
    ) -> None:
        self.model_viewset_test_case = model_viewset_test_case

    def bind_to_model_view(self, model_view: AbstractModelView) -> None:
        self.model_view = model_view
