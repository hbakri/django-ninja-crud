import uuid
from http import HTTPStatus

from ninja_crud.testing import APITestCase, APIViewTestScenario
from tests.test_app.schemas import ItemOut, Paged, TagOut
from tests.test_app.tests.base_test_case import BaseTestCase


class TestItemViewSet(APITestCase, BaseTestCase):
    def test_list_items(self):
        self.assertScenariosSucceed(
            method="GET",
            path="/api/items/",
            scenarios=[
                APIViewTestScenario(
                    request_headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"},
                    expected_response_status=HTTPStatus.OK,
                    expected_response_body_type=Paged[ItemOut],
                ),
                APIViewTestScenario(
                    query_parameters={"order_by": ["name"], "limit": 1},
                    request_headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"},
                    expected_response_status=HTTPStatus.OK,
                    expected_response_body_type=Paged[ItemOut],
                ),
                APIViewTestScenario(
                    request_headers={"HTTP_AUTHORIZATION": f"Bearer {999}"},
                    expected_response_status=HTTPStatus.UNAUTHORIZED,
                ),
            ],
        )

    def test_read_item(self):
        self.assertScenariosSucceed(
            method="GET",
            path="/api/items/{id}",
            scenarios=[
                APIViewTestScenario(
                    path_parameters={"id": self.item_1.id},
                    request_headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"},
                    expected_response_status=HTTPStatus.OK,
                    expected_response_body_type=ItemOut,
                    expected_response_body=ItemOut.from_orm(self.item_1).json(),
                ),
                APIViewTestScenario(
                    path_parameters={"id": uuid.uuid4()},
                    request_headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"},
                    expected_response_status=HTTPStatus.NOT_FOUND,
                ),
                APIViewTestScenario(
                    path_parameters={"id": self.item_1.id},
                    request_headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_2.id}"},
                    expected_response_status=HTTPStatus.FORBIDDEN,
                ),
                APIViewTestScenario(
                    path_parameters={"id": self.item_1.id},
                    expected_response_status=HTTPStatus.UNAUTHORIZED,
                ),
            ],
        )

    def test_update_item(self):
        self.assertScenariosSucceed(
            method="PUT",
            path="/api/items/{id}",
            scenarios=[
                APIViewTestScenario(
                    path_parameters={"id": self.item_1.id},
                    request_body={"name": "new-name", "description": "new-description"},
                    request_headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"},
                    expected_response_status=HTTPStatus.OK,
                    expected_response_body_type=ItemOut,
                    expected_response_body={
                        "id": str(self.item_1.id),
                        "collection_id": str(self.item_1.collection_id),
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
                    path_parameters={"id": self.item_1.id},
                    request_headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_2.id}"},
                    expected_response_status=HTTPStatus.FORBIDDEN,
                ),
                APIViewTestScenario(
                    path_parameters={"id": self.item_1.id},
                    expected_response_status=HTTPStatus.UNAUTHORIZED,
                ),
            ],
        )

    def test_delete_item(self):
        self.assertScenariosSucceed(
            method="DELETE",
            path="/api/items/{id}",
            scenarios=[
                APIViewTestScenario(
                    path_parameters={"id": self.item_1.id},
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
                    path_parameters={"id": self.item_1.id},
                    request_headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_2.id}"},
                    expected_response_status=HTTPStatus.FORBIDDEN,
                ),
                APIViewTestScenario(
                    path_parameters={"id": self.item_1.id},
                    expected_response_status=HTTPStatus.UNAUTHORIZED,
                ),
            ],
        )

    def test_list_tags(self):
        self.assertScenariosSucceed(
            method="GET",
            path="/api/items/{id}/tags/",
            scenarios=[
                APIViewTestScenario(
                    path_parameters={"id": self.item_1.id},
                    request_headers={"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"},
                    expected_response_status=HTTPStatus.OK,
                    expected_response_body_type=Paged[TagOut],
                ),
                APIViewTestScenario(
                    path_parameters={"id": self.item_1.id},
                    expected_response_status=HTTPStatus.UNAUTHORIZED,
                ),
            ],
        )
