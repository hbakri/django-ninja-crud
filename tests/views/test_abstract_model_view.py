from unittest.mock import patch

from django.test import TestCase

from ninja_crud.views import AbstractModelView


class TestAbstractModelView(TestCase):
    def test_sanitize_and_merge_router_kwargs(self):
        router_kwargs = {"exclude_unset": True, "other": "value"}
        sanitized_router_kwargs = AbstractModelView._clean_router_kwargs(router_kwargs)

        self.assertDictEqual(sanitized_router_kwargs, router_kwargs)

    def test_sanitize_and_merge_router_kwargs_with_path(self):
        router_kwargs = {"path": "/new_path"}
        with patch("ninja_crud.views.abstract_view.logger") as mock_logger:
            sanitized_router_kwargs = AbstractModelView._clean_router_kwargs(
                router_kwargs
            )
            mock_logger.warning.assert_called_once()

        self.assertDictEqual(sanitized_router_kwargs, {})
