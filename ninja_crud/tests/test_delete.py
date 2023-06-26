import random
import uuid
from http import HTTPStatus
from typing import Union
from uuid import UUID

from django.db.models import Model
from django.http import HttpResponse
from django.urls import reverse

from ninja_crud.tests.test_abstract import AbstractModelViewTest, Credentials
from ninja_crud.views import utils
from ninja_crud.views.delete import DeleteModelView


class DeleteModelViewTest(AbstractModelViewTest):
    model_view = DeleteModelView

    def delete_model(self, id: Union[int, UUID], credentials: dict) -> HttpResponse:
        kwargs = {"id": id}
        url_name = utils.to_snake_case(self.model_view_set.model.__name__)
        return self.client.delete(
            reverse(f"api:{url_name}", kwargs=kwargs),
            content_type="application/json",
            **credentials,
        )

    def assert_response_is_ok(self, response: HttpResponse):
        self.test_case.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
        self.test_case.assertEqual(response.content, b"")

    def test_delete_model_ok(self):
        credentials: Credentials = self.get_credentials(self.test_case)
        instance: Model = self.get_instance(self.test_case)
        response = self.delete_model(id=instance.pk, credentials=credentials.ok)
        self.assert_response_is_ok(response)

    def test_delete_model_unauthorized(self):
        credentials: Credentials = self.get_credentials(self.test_case)
        if credentials.unauthorized is None:
            self.test_case.skipTest("No unauthorized credentials provided")
        instance: Model = self.get_instance(self.test_case)
        response = self.delete_model(
            id=instance.pk, credentials=credentials.unauthorized
        )
        self.assert_response_is_bad_request(
            response, status_code=HTTPStatus.UNAUTHORIZED
        )

    def test_delete_model_not_found(self):
        credentials: Credentials = self.get_credentials(self.test_case)
        instance: Model = self.get_instance(self.test_case)
        random_id = (
            uuid.uuid4() if type(instance.pk) is UUID else random.randint(1000, 9999)
        )
        response = self.delete_model(id=random_id, credentials=credentials.ok)
        self.assert_response_is_bad_request(response, status_code=HTTPStatus.NOT_FOUND)

    def test_delete_model_forbidden(self):
        credentials: Credentials = self.get_credentials(self.test_case)
        if credentials.forbidden is None:
            self.test_case.skipTest("No forbidden credentials provided")
        instance: Model = self.get_instance(self.test_case)
        response = self.delete_model(id=instance.pk, credentials=credentials.forbidden)
        self.assert_response_is_bad_request(response, status_code=HTTPStatus.FORBIDDEN)
