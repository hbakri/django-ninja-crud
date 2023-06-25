import json
from http import HTTPStatus
from typing import Callable, Union
from uuid import UUID

from django.db.models import Model
from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse

from ninja_crud import utils
from ninja_crud.tests.test_abstract import AbstractModelViewTest, Credentials, Payloads
from ninja_crud.views.create import CreateModelView


class CreateModelViewTest(AbstractModelViewTest):
    model_view = CreateModelView

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

    def create_model(
        self, id: Union[int, UUID], data: dict, credentials: dict
    ) -> HttpResponse:
        model_view: CreateModelView = self.get_model_view()
        model_name = utils.to_snake_case(self.model_view_set.model.__name__)
        if model_view.detail:
            related_model_name = utils.to_snake_case(model_view.related_model.__name__)
            url_name = f"{model_name}_{related_model_name}s"
            kwargs = {"id": id}
        else:
            url_name = f"{model_name}s"
            kwargs = {}

        return self.client.post(
            reverse(f"api:{url_name}", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **credentials,
        )

    def assert_response_is_ok(self, response: HttpResponse):
        self.test_case.assertEqual(response.status_code, HTTPStatus.CREATED)
        content = json.loads(response.content)

        model_view: CreateModelView = self.get_model_view()
        if model_view.detail:
            model = model_view.related_model
        else:
            model = self.model_view_set.model
        self.assert_content_equals_schema(
            content,
            queryset=model.objects.get_queryset(),
            output_schema=model_view.output_schema,
        )

    def test_create_model_ok(self):
        credentials: Credentials = self.get_credentials(self.test_case)
        instance: Model = self.get_instance(self.test_case)
        response = self.create_model(
            id=instance.pk, data=self.payloads.ok, credentials=credentials.ok
        )
        self.assert_response_is_ok(response)

    def test_create_model_bad_request(self):
        if self.payloads.bad_request is None:
            self.test_case.skipTest("No bad request payload provided")
        credentials: Credentials = self.get_credentials(self.test_case)
        instance: Model = self.get_instance(self.test_case)
        response = self.create_model(
            id=instance.pk, data=self.payloads.bad_request, credentials=credentials.ok
        )
        self.assert_response_is_bad_request(
            response, status_code=HTTPStatus.BAD_REQUEST
        )

    def test_create_model_conflict(self):
        if self.payloads.conflict is None:
            self.test_case.skipTest("No conflict payload provided")
        credentials: Credentials = self.get_credentials(self.test_case)
        instance: Model = self.get_instance(self.test_case)
        response = self.create_model(
            id=instance.pk, data=self.payloads.conflict, credentials=credentials.ok
        )
        self.assert_response_is_bad_request(response, status_code=HTTPStatus.CONFLICT)

    def test_create_model_unauthorized(self):
        credentials: Credentials = self.get_credentials(self.test_case)
        if credentials.unauthorized is None:
            self.test_case.skipTest("No unauthorized credentials provided")
        instance: Model = self.get_instance(self.test_case)
        response = self.create_model(
            id=instance.pk, data=self.payloads.ok, credentials=credentials.unauthorized
        )
        self.assert_response_is_bad_request(
            response, status_code=HTTPStatus.UNAUTHORIZED
        )

    def test_create_model_forbidden(self):
        credentials: Credentials = self.get_credentials(self.test_case)
        if credentials.forbidden is None:
            self.test_case.skipTest("No forbidden credentials provided")
        instance: Model = self.get_instance(self.test_case)
        response = self.create_model(
            id=instance.pk, data=self.payloads.ok, credentials=credentials.forbidden
        )
        self.assert_response_is_bad_request(response, status_code=HTTPStatus.FORBIDDEN)
