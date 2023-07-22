import logging
from typing import List, Type

from ninja_crud.tests.test_abstract import AbstractModelViewTest
from ninja_crud.views import AbstractModelView, ModelViewSet

logger = logging.getLogger(__name__)


class ModelViewSetTestMatcher:
    @staticmethod
    def get_associated_model_view(
        model_view_set_class: Type[ModelViewSet],
        test_attr_name: str,
        test_attr_value: AbstractModelViewTest,
    ) -> AbstractModelView:
        for attr_name in dir(model_view_set_class):
            attr_value = getattr(model_view_set_class, attr_name)
            if (
                isinstance(attr_value, test_attr_value.model_view_class)
                and test_attr_name == f"test_{attr_name}"
            ):
                return attr_value

        raise ValueError(
            f"Could not find associated model view for test '{test_attr_name}'"
        )  # pragma: no cover

    @staticmethod
    def assert_all_model_views_are_associated(
        model_view_set_class: Type[ModelViewSet],
        associated_model_views: List[AbstractModelView],
    ) -> None:
        for attr_name in dir(model_view_set_class):
            attr_value = getattr(model_view_set_class, attr_name)
            if isinstance(attr_value, AbstractModelView):
                if attr_value not in associated_model_views:  # pragma: no cover
                    logger.warning(
                        f"Model view {model_view_set_class.__name__}.{attr_name} is not associated with any test"
                    )
