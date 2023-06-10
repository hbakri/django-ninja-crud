import json
import uuid
from http import HTTPStatus
from typing import Optional
from uuid import UUID

from django.db.models import Model
from django.http import HttpResponse
from django.urls import reverse

from ninja_crud import utils
from ninja_crud.tests.test_abstract import AbstractModelViewTest, Credentials
from ninja_crud.views.retrieve import RetrieveModelView


class RetrieveModelViewTest(AbstractModelViewTest):
    model_view = RetrieveModelView

    def retrieve_model(self, id: UUID, credentials: Optional[dict]) -> HttpResponse:
        if credentials is None:
            credentials = {}

        kwargs = {"id": id}
        url_name = utils.to_snake_case(self.model_view_set.model.__name__)
        return self.client.get(
            reverse(f"api:{url_name}", kwargs=kwargs),
            content_type="application/json",
            **credentials,
        )

    def assert_response_is_ok(self, response: HttpResponse, id: UUID):
        self.test_case.assertEqual(response.status_code, HTTPStatus.OK)
        content = json.loads(response.content)

        model_view: RetrieveModelView = self.get_model_view()

        if model_view.get_queryset is not None:
            queryset = model_view.get_queryset(id)
        else:
            queryset = self.model_view_set.model.objects.get_queryset()

        self.assert_content_equals_schema(
            content,
            queryset=queryset,
            output_schema=model_view.output_schema,
        )

    def test_retrieve_model_ok(self):
        credentials: Credentials = self.get_credentials(self.test_case)
        instance: Model = self.get_instance(self.test_case)
        response = self.retrieve_model(id=instance.pk, credentials=credentials.ok)
        self.assert_response_is_ok(response, id=instance.pk)

    def test_retrieve_model_unauthorized(self):
        credentials: Credentials = self.get_credentials(self.test_case)
        if credentials.unauthorized is None:
            self.test_case.skipTest("No unauthorized credentials provided")
        instance: Model = self.get_instance(self.test_case)
        response = self.retrieve_model(id=instance.pk, credentials=None)
        self.assert_response_is_bad_request(
            response, status_code=HTTPStatus.UNAUTHORIZED
        )

    def test_retrieve_model_not_found(self):
        credentials: Credentials = self.get_credentials(self.test_case)
        response = self.retrieve_model(id=uuid.uuid4(), credentials=credentials.ok)
        self.assert_response_is_bad_request(response, status_code=HTTPStatus.NOT_FOUND)

    def test_retrieve_model_forbidden(self):
        credentials: Credentials = self.get_credentials(self.test_case)
        if credentials.forbidden is None:
            self.test_case.skipTest("No forbidden credentials provided")
        instance: Model = self.get_instance(self.test_case)
        response = self.retrieve_model(
            id=instance.pk, credentials=credentials.forbidden
        )
        self.assert_response_is_bad_request(response, status_code=HTTPStatus.FORBIDDEN)
