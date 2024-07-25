from http import HTTPStatus
from typing import List

from ninja_crud.testing import APITestCase, APIViewTestScenario
from tests.test_app.schemas import UserResponseBody
from tests.test_app.tests.base_test_case import BaseTestCase


class TestUserViewSet(APITestCase, BaseTestCase):
    def test_list_users(self):
        self.assertScenariosSucceed(
            method="GET",
            path="/api/users/",
            scenarios=[
                APIViewTestScenario(
                    expected_response_status=HTTPStatus.OK,
                    expected_response_body_type=List[UserResponseBody],
                ),
            ],
        )

    def test_create_user(self):
        self.assertScenariosSucceed(
            method="POST",
            path="/api/users/",
            scenarios=[
                APIViewTestScenario(
                    request_body={
                        "username": "new-user",
                        "email": "user@email.com",
                        "password": "new-password",
                        "groups": [self.group_1.id, self.group_2.id],
                    },
                    expected_response_status=HTTPStatus.CREATED,
                    expected_response_body_type=UserResponseBody,
                ),
                APIViewTestScenario(
                    request_body={
                        "username": "new-user",
                        "password": "new-password",
                    },
                    expected_response_status=HTTPStatus.BAD_REQUEST,
                ),
                APIViewTestScenario(
                    request_body={
                        "username": self.user_2.username,
                        "email": "user@email.com",
                        "password": "new-password",
                    },
                    expected_response_status=HTTPStatus.CONFLICT,
                ),
            ],
        )

    def test_read_user(self):
        self.assertScenariosSucceed(
            method="GET",
            path="/api/users/{id}",
            scenarios=[
                APIViewTestScenario(
                    path_parameters={"id": self.user_1.id},
                    expected_response_status=HTTPStatus.OK,
                    expected_response_body_type=UserResponseBody,
                    expected_response_body=UserResponseBody.from_orm(
                        self.user_1
                    ).json(),
                ),
                APIViewTestScenario(
                    path_parameters={"id": self.user_2.id},
                    expected_response_status=HTTPStatus.OK,
                    expected_response_body_type=UserResponseBody,
                    expected_response_body=UserResponseBody.from_orm(
                        self.user_2
                    ).json(),
                ),
                APIViewTestScenario(
                    path_parameters={"id": 999},
                    expected_response_status=HTTPStatus.NOT_FOUND,
                ),
            ],
        )

    def test_update_user(self):
        self.assertScenariosSucceed(
            method="PUT",
            path="/api/users/{id}",
            scenarios=[
                APIViewTestScenario(
                    path_parameters={"id": self.user_1.id},
                    request_body={
                        "username": "new-user",
                        "email": "user@email.com",
                        "password": "new-password",
                        "groups": [self.group_1.id, self.group_2.id],
                    },
                    expected_response_status=HTTPStatus.OK,
                ),
                APIViewTestScenario(
                    path_parameters={"id": self.user_1.id},
                    request_body={
                        "username": "new-user",
                        "password": "new-password",
                    },
                    expected_response_status=HTTPStatus.BAD_REQUEST,
                ),
                APIViewTestScenario(
                    path_parameters={"id": self.user_1.id},
                    request_body={
                        "username": self.user_2.username,
                        "email": "user@email.com",
                        "password": "new-password",
                    },
                    expected_response_status=HTTPStatus.CONFLICT,
                ),
                APIViewTestScenario(
                    path_parameters={"id": 999},
                    request_body={
                        "username": "new-user",
                        "email": "user@email.com",
                        "password": "new-password",
                        "groups": [self.group_1.id, self.group_2.id],
                    },
                    expected_response_status=HTTPStatus.NOT_FOUND,
                ),
            ],
            default_assertions=lambda response, scenario: None,
        )

    def test_delete_user(self):
        self.assertScenariosSucceed(
            method="DELETE",
            path="/api/users/{id}",
            scenarios=[
                APIViewTestScenario(
                    path_parameters={"id": self.user_1.id},
                    expected_response_status=HTTPStatus.NO_CONTENT,
                    expected_response_body=b"",
                ),
                APIViewTestScenario(
                    path_parameters={"id": self.user_2.id},
                    expected_response_status=HTTPStatus.NO_CONTENT,
                    expected_response_body=b"",
                ),
                APIViewTestScenario(
                    path_parameters={"id": 999},
                    expected_response_status=HTTPStatus.NOT_FOUND,
                ),
            ],
        )
