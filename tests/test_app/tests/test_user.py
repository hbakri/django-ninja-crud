from typing import Union

from django.contrib.auth.models import User
from django.test import TestCase

from ninja_crud.tests import (
    CreateModelViewTest,
    DeleteModelViewTest,
    ListModelViewTest,
    ModelViewSetTest,
    Payloads,
    RetrieveModelViewTest,
    UpdateModelViewTest,
)
from tests.test_app.views.view_user import UserViewSet


class UserViewSetTest(ModelViewSetTest, TestCase):
    model_view_set = UserViewSet
    user_1: User
    user_2: User

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user_1 = User.objects.create(
            username="user-1", email="user.1@email.com", password="password-1"
        )
        cls.user_2 = User.objects.create(
            username="user-2", email="user.2@email.com", password="password-2"
        )

    def get_instance(self: Union["UserViewSetTest", TestCase]):
        return self.user_1

    user_payloads = Payloads(
        ok={
            "username": "new-user",
            "email": "user@email.com",
            "password": "new-password",
        },
        bad_request={"username": "new-user", "password": "new-password"},
        conflict={
            "username": "user-2",
            "email": "user@email.com",
            "password": "new-password",
        },
    )

    test_list = ListModelViewTest(instance_getter=get_instance)
    test_create = CreateModelViewTest(
        payloads=user_payloads, instance_getter=get_instance
    )
    test_retrieve = RetrieveModelViewTest(instance_getter=get_instance)
    test_update = UpdateModelViewTest(
        payloads=user_payloads, instance_getter=get_instance
    )
    test_delete = DeleteModelViewTest(instance_getter=get_instance)
