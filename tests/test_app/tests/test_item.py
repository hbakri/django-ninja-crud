from typing import Union

from django.test import TestCase

from ninja_crud.tests import (
    Credentials,
    DeleteModelViewTest,
    ListModelViewTest,
    ModelViewSetTest,
    Payloads,
    RetrieveModelViewTest,
    UpdateModelViewTest,
)
from tests.test_app.tests.test_base import BaseTestCase
from tests.test_app.views.view_item import ItemViewSet


class ItemViewSetTest(ModelViewSetTest, BaseTestCase):
    model_view_set = ItemViewSet

    def get_instance(self: Union["ItemViewSetTest", TestCase]):
        return self.item

    def get_credentials_ok(self: Union["ItemViewSetTest", TestCase]):
        return Credentials(
            ok={"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"}, unauthorized={}
        )

    def get_credentials_ok_forbidden(self: Union["ItemViewSetTest", TestCase]):
        return Credentials(
            ok={"HTTP_AUTHORIZATION": f"Bearer {self.user_1.id}"},
            unauthorized={},
            forbidden={"HTTP_AUTHORIZATION": f"Bearer {self.user_2.id}"},
        )

    item_payloads = Payloads(
        ok={"name": "new-name", "description": "new-description"},
    )

    test_list = ListModelViewTest(
        instance_getter=get_instance,
        credentials_getter=get_credentials_ok,
    )
    test_retrieve = RetrieveModelViewTest(
        instance_getter=get_instance,
        credentials_getter=get_credentials_ok_forbidden,
    )
    test_update = UpdateModelViewTest(
        payloads=item_payloads,
        instance_getter=get_instance,
        credentials_getter=get_credentials_ok_forbidden,
    )
    test_delete = DeleteModelViewTest(
        instance_getter=get_instance, credentials_getter=get_credentials_ok_forbidden
    )

    test_list_tags = ListModelViewTest(
        instance_getter=get_instance,
        credentials_getter=get_credentials_ok,
    )
