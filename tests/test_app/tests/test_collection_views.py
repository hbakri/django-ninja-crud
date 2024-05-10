import uuid
from http import HTTPStatus

from ninja_crud.testing import APITestCase, APIViewTestScenario
from tests.test_app.schemas import CollectionOut, ItemOut, Paged
from tests.test_app.tests.base_test_case import BaseTestCase


class TestCollectionViewSet(APITestCase, BaseTestCase):
    def test_list_collections(self):
        self.assertScenariosSucceed(
            method="GET",
            path="/api/collections/",
            scenarios=[
                APIViewTestScenario(
                    request_headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"},
                    expected_response_status=HTTPStatus.OK,
                    expected_response_body_type=Paged[CollectionOut],
                ),
                APIViewTestScenario(
                    query_parameters={
                        "name": "collection-1",
                        "order_by": ["name"],
                        "limit": 1,
                    },
                    request_headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"},
                    expected_response_status=HTTPStatus.OK,
                    expected_response_body_type=Paged[CollectionOut],
                ),
                APIViewTestScenario(
                    query_parameters={"order_by": ["unknown_field"]},
                    request_headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"},
                    expected_response_status=HTTPStatus.BAD_REQUEST,
                ),
                APIViewTestScenario(
                    expected_response_status=HTTPStatus.UNAUTHORIZED,
                ),
            ],
        )

    def test_create_collection(self):
        self.assertScenariosSucceed(
            method="POST",
            path="/api/collections/",
            scenarios=[
                APIViewTestScenario(
                    request_headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"},
                    request_body={"name": "new-name", "description": "new-description"},
                    expected_response_status=HTTPStatus.CREATED,
                    expected_response_body_type=CollectionOut,
                ),
                APIViewTestScenario(
                    request_headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"},
                    request_body={"description": "new-description"},
                    expected_response_status=HTTPStatus.BAD_REQUEST,
                ),
                APIViewTestScenario(
                    request_headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"},
                    request_body={"name": "collection-2"},
                    expected_response_status=HTTPStatus.CONFLICT,
                ),
                APIViewTestScenario(
                    expected_response_status=HTTPStatus.UNAUTHORIZED,
                ),
            ],
        )

    def test_read_collection(self):
        self.assertScenariosSucceed(
            method="GET",
            path="/api/collections/{id}",
            scenarios=[
                APIViewTestScenario(
                    path_parameters={"id": self.collection_1.id},
                    request_headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"},
                    expected_response_status=HTTPStatus.OK,
                    expected_response_body_type=CollectionOut,
                    expected_response_body=CollectionOut.from_orm(
                        self.collection_1
                    ).json(),
                ),
                APIViewTestScenario(
                    path_parameters={"id": uuid.uuid4()},
                    request_headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"},
                    expected_response_status=HTTPStatus.NOT_FOUND,
                ),
                APIViewTestScenario(
                    path_parameters={"id": self.collection_1.id},
                    expected_response_status=HTTPStatus.UNAUTHORIZED,
                ),
            ],
        )

    def test_update_collection(self):
        self.assertScenariosSucceed(
            method="PUT",
            path="/api/collections/{id}",
            scenarios=[
                APIViewTestScenario(
                    path_parameters={"id": self.collection_1.id},
                    request_headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"},
                    request_body={"name": "new-name", "description": "new-description"},
                    expected_response_status=HTTPStatus.OK,
                    expected_response_body_type=CollectionOut,
                    expected_response_body={
                        "id": str(self.collection_1.id),
                        "name": "new-name",
                        "description": "new-description",
                    },
                ),
                APIViewTestScenario(
                    path_parameters={"id": uuid.uuid4()},
                    request_headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"},
                    expected_response_status=HTTPStatus.NOT_FOUND,
                ),
                APIViewTestScenario(
                    path_parameters={"id": self.collection_1.id},
                    request_headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"},
                    request_body={"description": "new-description"},
                    expected_response_status=HTTPStatus.BAD_REQUEST,
                ),
                APIViewTestScenario(
                    path_parameters={"id": self.collection_1.id},
                    request_headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"},
                    request_body={"name": "collection-2"},
                    expected_response_status=HTTPStatus.CONFLICT,
                ),
                APIViewTestScenario(
                    path_parameters={"id": self.collection_1.id},
                    request_headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_2.id}"},
                    expected_response_status=HTTPStatus.FORBIDDEN,
                ),
                APIViewTestScenario(
                    path_parameters={"id": self.collection_1.id},
                    expected_response_status=HTTPStatus.UNAUTHORIZED,
                ),
            ],
        )

    def test_delete_collection(self):
        self.assertScenariosSucceed(
            method="DELETE",
            path="/api/collections/{id}",
            scenarios=[
                APIViewTestScenario(
                    path_parameters={"id": self.collection_1.id},
                    request_headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"},
                    expected_response_status=HTTPStatus.NO_CONTENT,
                    expected_response_body=b"",
                ),
                APIViewTestScenario(
                    path_parameters={"id": uuid.uuid4()},
                    request_headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"},
                    expected_response_status=HTTPStatus.NOT_FOUND,
                ),
                APIViewTestScenario(
                    path_parameters={"id": self.collection_1.id},
                    request_headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_2.id}"},
                    expected_response_status=HTTPStatus.FORBIDDEN,
                ),
                APIViewTestScenario(
                    path_parameters={"id": self.collection_1.id},
                    expected_response_status=HTTPStatus.UNAUTHORIZED,
                ),
            ],
        )

    def test_list_collection_items(self):
        self.assertScenariosSucceed(
            method="GET",
            path="/api/collections/{id}/items/",
            scenarios=[
                APIViewTestScenario(
                    path_parameters={"id": self.collection_1.id},
                    request_headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"},
                    expected_response_status=HTTPStatus.OK,
                    expected_response_body_type=Paged[ItemOut],
                ),
                APIViewTestScenario(
                    path_parameters={"id": uuid.uuid4()},
                    request_headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"},
                    expected_response_status=HTTPStatus.NOT_FOUND,
                ),
                APIViewTestScenario(
                    path_parameters={"id": self.collection_1.id},
                    request_headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_2.id}"},
                    expected_response_status=HTTPStatus.FORBIDDEN,
                ),
                APIViewTestScenario(
                    path_parameters={"id": self.collection_1.id},
                    expected_response_status=HTTPStatus.UNAUTHORIZED,
                ),
            ],
        )

    def test_create_collection_item(self):
        self.assertScenariosSucceed(
            method="POST",
            path="/api/collections/{id}/items/",
            scenarios=[
                APIViewTestScenario(
                    path_parameters={"id": self.collection_1.id},
                    request_headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"},
                    request_body={"name": "new-name", "description": "new-description"},
                    expected_response_status=HTTPStatus.CREATED,
                    expected_response_body_type=ItemOut,
                ),
                APIViewTestScenario(
                    path_parameters={"id": uuid.uuid4()},
                    request_headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"},
                    expected_response_status=HTTPStatus.NOT_FOUND,
                ),
                APIViewTestScenario(
                    path_parameters={"id": self.collection_1.id},
                    request_headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_2.id}"},
                    expected_response_status=HTTPStatus.FORBIDDEN,
                ),
                APIViewTestScenario(
                    path_parameters={"id": self.collection_1.id},
                    expected_response_status=HTTPStatus.UNAUTHORIZED,
                ),
            ],
        )
