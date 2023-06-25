import json
import random
import uuid
from http import HTTPStatus
from typing import Callable, Union
from uuid import UUID

from django.db.models import Model
from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse

from ninja_crud import utils
from ninja_crud.tests.test_abstract import AbstractModelViewTest, Credentials, Payloads
from ninja_crud.views.update import UpdateModelView


class UpdateModelViewTest(AbstractModelViewTest):
    model_view = UpdateModelView

    def __init__(
        self,
        payloads: Payloads,
        instance_getter: Callable[[TestCase], Model],
        credentials_getter: Callable[[TestCase], Credentials] = None,
    ) -> None:
        super().__init__(
            instance_getter=instance_getter, credentials_getter=credentials_getter
        )
        self.payloads = payloads

    def update_model(
        self, id: Union[int, UUID], data: dict, credentials: dict
    ) -> HttpResponse:
        kwargs = {"id": id}
        url_name = utils.to_snake_case(self.model_view_set.model.__name__)
        return self.client.put(
            reverse(f"api:{url_name}", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **credentials,
        )

    def assert_response_is_ok(self, response: HttpResponse):
        self.test_case.assertEqual(response.status_code, HTTPStatus.OK)
        content = json.loads(response.content)

        model_view: UpdateModelView = self.get_model_view()
        self.assert_content_equals_schema(
            content,
            queryset=self.model_view_set.model.objects.get_queryset(),
            output_schema=model_view.output_schema,
        )

    def test_update_model_ok(self):
        credentials: Credentials = self.get_credentials(self.test_case)
        instance: Model = self.get_instance(self.test_case)
        response = self.update_model(
            id=instance.pk, data=self.payloads.ok, credentials=credentials.ok
        )
        self.assert_response_is_ok(response)

    def test_update_model_bad_request(self):
        if self.payloads.bad_request is None:
            self.test_case.skipTest("No bad request payload provided")
        credentials: Credentials = self.get_credentials(self.test_case)
        instance: Model = self.get_instance(self.test_case)
        response = self.update_model(
            id=instance.pk, data=self.payloads.bad_request, credentials=credentials.ok
        )
        self.assert_response_is_bad_request(
            response, status_code=HTTPStatus.BAD_REQUEST
        )

    def test_update_model_conflict(self):
        if self.payloads.conflict is None:
            self.test_case.skipTest("No conflict payload provided")
        credentials: Credentials = self.get_credentials(self.test_case)
        instance: Model = self.get_instance(self.test_case)
        response = self.update_model(
            id=instance.pk, data=self.payloads.conflict, credentials=credentials.ok
        )
        self.assert_response_is_bad_request(response, status_code=HTTPStatus.CONFLICT)

    def test_update_model_unauthorized(self):
        credentials: Credentials = self.get_credentials(self.test_case)
        if credentials.unauthorized is None:
            self.test_case.skipTest("No unauthorized credentials provided")
        instance: Model = self.get_instance(self.test_case)
        response = self.update_model(
            id=instance.pk, data=self.payloads.ok, credentials=credentials.unauthorized
        )
        self.assert_response_is_bad_request(
            response, status_code=HTTPStatus.UNAUTHORIZED
        )

    def test_update_model_not_found(self):
        credentials: Credentials = self.get_credentials(self.test_case)
        instance: Model = self.get_instance(self.test_case)
        random_id = (
            uuid.uuid4() if type(instance.pk) is UUID else random.randint(1000, 9999)
        )
        response = self.update_model(
            id=random_id, data=self.payloads.ok, credentials=credentials.ok
        )
        self.assert_response_is_bad_request(response, status_code=HTTPStatus.NOT_FOUND)

    def test_update_model_forbidden(self):
        credentials: Credentials = self.get_credentials(self.test_case)
        if credentials.forbidden is None:
            self.test_case.skipTest("No forbidden credentials provided")
        instance: Model = self.get_instance(self.test_case)
        response = self.update_model(
            id=instance.pk, data=self.payloads.ok, credentials=credentials.forbidden
        )
        self.assert_response_is_bad_request(response, status_code=HTTPStatus.FORBIDDEN)
