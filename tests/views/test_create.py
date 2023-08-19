from unittest.mock import MagicMock

from django.test import TestCase

from ninja_crud.views.create import CreateModelView
from tests.test_app.models import Collection
from tests.test_app.schemas import ItemIn, ItemOut


class CreateModelViewTest(TestCase):
    def test_register_route_with_router_kwargs(self):
        router_mock = MagicMock()
        model_view = CreateModelView(
            input_schema=ItemIn,
            output_schema=ItemOut,
            router_kwargs={"exclude_unset": True},
        )

        model_view.register_route(router_mock, Collection)

        router_mock.post.assert_called_once()
        self.assertTrue(router_mock.post.call_args[1]["exclude_unset"])
