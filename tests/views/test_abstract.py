from typing import List
from unittest.mock import patch

from django.test import TestCase
from ninja import Schema

from ninja_crud.views import AbstractModelView


class TestAbstractModelView(TestCase):
    def test_sanitize_and_merge_router_kwargs(self):
        custom_router_kwargs = {"exclude_unset": True, "other": "value"}
        default_router_kwargs = {
            "path": "/",
            "response": List[Schema],
            "operation_id": "list_objects",
            "summary": "List objects",
        }
        router_kwargs = AbstractModelView._sanitize_and_merge_router_kwargs(
            default_router_kwargs=default_router_kwargs,
            custom_router_kwargs=custom_router_kwargs,
        )

        self.assertDictEqual(
            router_kwargs,
            {**default_router_kwargs, **custom_router_kwargs},
        )

    def test_sanitize_and_merge_router_kwargs_with_path(self):
        custom_router_kwargs = {"path": "/new_path"}
        default_router_kwargs = {
            "path": "/",
            "response": List[Schema],
            "operation_id": "list_objects",
            "summary": "List objects",
        }
        with patch("ninja_crud.views.abstract.logger") as mock_logger:
            router_kwargs = AbstractModelView._sanitize_and_merge_router_kwargs(
                default_router_kwargs=default_router_kwargs,
                custom_router_kwargs=custom_router_kwargs,
            )
            mock_logger.warning.assert_called_once()

        self.assertDictEqual(router_kwargs, default_router_kwargs)
