from typing import List
from unittest import mock

import ninja
from django.test import TestCase
from pydantic import BaseModel

from ninja_crud import views, viewsets
from tests.test_app.models import Collection


class TestAPIViewSet(TestCase):
    def setUp(self):
        class CollectionRequestBody(BaseModel):
            name: str

        class CollectionResponseBody(BaseModel):
            id: int
            name: str

        class CollectionViewSet(viewsets.APIViewSet):
            model = Collection
            default_request_body = CollectionRequestBody
            default_response_body = CollectionResponseBody

            list_view = views.ListView()
            create_view = views.CreateView()

        self.CollectionRequestBody = CollectionRequestBody
        self.CollectionResponseBody = CollectionResponseBody
        self.CollectionViewSet = CollectionViewSet

    def test_add_views_to_api(self):
        mock_api = mock.Mock(spec=ninja.NinjaAPI)
        mock_api.default_router = mock.Mock(spec=ninja.Router)
        mock_api.default_router.add_api_operation = mock.Mock()

        self.CollectionViewSet.add_views_to(mock_api)

        mock_api.default_router.add_api_operation.assert_has_calls(
            [
                mock.call(
                    path="/",
                    methods=["GET"],
                    view_func=mock.ANY,
                    response={200: List[self.CollectionViewSet.default_response_body]},
                ),
                mock.call(
                    path="/",
                    methods=["POST"],
                    view_func=mock.ANY,
                    response={201: self.CollectionViewSet.default_response_body},
                ),
            ]
        )

    def test_add_views_to_router(self):
        mock_router = mock.Mock(spec=ninja.Router)
        mock_router.add_api_operation = mock.Mock()

        self.CollectionViewSet.add_views_to(mock_router)

        mock_router.add_api_operation.assert_has_calls(
            [
                mock.call(
                    path="/",
                    methods=["GET"],
                    view_func=mock.ANY,
                    response={200: List[self.CollectionViewSet.default_response_body]},
                ),
                mock.call(
                    path="/",
                    methods=["POST"],
                    view_func=mock.ANY,
                    response={201: self.CollectionViewSet.default_response_body},
                ),
            ]
        )

    def test_add_views_to_api_with_class_attribute(self):
        mock_api = mock.Mock(spec=ninja.NinjaAPI)
        mock_api.default_router = mock.Mock(spec=ninja.Router)
        mock_api.default_router.add_api_operation = mock.Mock()

        class CollectionViewSet(viewsets.APIViewSet):
            api = mock_api
            model = Collection
            default_request_body = self.CollectionRequestBody
            default_response_body = self.CollectionResponseBody

            list_view = views.ListView()
            create_view = views.CreateView()

        mock_api.default_router.add_api_operation.assert_has_calls(
            [
                mock.call(
                    path="/",
                    methods=["GET"],
                    view_func=mock.ANY,
                    response={200: List[CollectionViewSet.default_response_body]},
                ),
                mock.call(
                    path="/",
                    methods=["POST"],
                    view_func=mock.ANY,
                    response={201: CollectionViewSet.default_response_body},
                ),
            ]
        )

    def test_add_views_to_router_with_class_attribute(self):
        mock_router = mock.Mock(spec=ninja.Router)
        mock_router.add_api_operation = mock.Mock()

        class CollectionViewSet(viewsets.APIViewSet):
            router = mock_router
            model = Collection
            default_request_body = self.CollectionRequestBody
            default_response_body = self.CollectionResponseBody

            list_view = views.ListView()
            create_view = views.CreateView()

        mock_router.add_api_operation.assert_has_calls(
            [
                mock.call(
                    path="/",
                    methods=["GET"],
                    view_func=mock.ANY,
                    response={200: List[CollectionViewSet.default_response_body]},
                ),
                mock.call(
                    path="/",
                    methods=["POST"],
                    view_func=mock.ANY,
                    response={201: CollectionViewSet.default_response_body},
                ),
            ]
        )
