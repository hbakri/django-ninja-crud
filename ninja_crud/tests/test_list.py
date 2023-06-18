import json
from http import HTTPStatus
from uuid import UUID

from django.db.models import Model
from django.http import HttpResponse
from django.urls import reverse

from ninja_crud import utils
from ninja_crud.tests.test_abstract import AbstractModelViewTest, Credentials
from ninja_crud.views.list import ListModelView


class ListModelViewTest(AbstractModelViewTest):
    model_view = ListModelView

    def list_model(self, id: UUID, credentials: dict) -> HttpResponse:
        model_view: ListModelView = self.get_model_view()
        model_name = utils.to_snake_case(self.model_view_set.model.__name__)
        if model_view.is_instance_view:
            related_model_name = utils.to_snake_case(model_view.related_model.__name__)
            url_name = f"{model_name}_{related_model_name}s"
            kwargs = {"id": id}
        else:
            url_name = f"{model_name}s"
            kwargs = {}

        response = self.client.get(
            reverse(f"api:{url_name}", kwargs=kwargs),
            content_type="application/json",
            **credentials,
        )
        return response

    def assert_response_is_ok(self, response: HttpResponse, id: UUID):
        self.test_case.assertEqual(response.status_code, HTTPStatus.OK)
        content = json.loads(response.content)

        model_view: ListModelView = self.get_model_view()

        if model_view.is_instance_view:
            if model_view.get_queryset is not None:
                queryset = model_view.get_queryset(id)
            else:
                queryset = model_view.related_model.objects.get_queryset()
        else:
            if model_view.get_queryset is not None:
                queryset = model_view.get_queryset()
            else:
                queryset = self.model_view_set.model.objects.get_queryset()

        self.assert_content_equals_schema_list(
            content, queryset=queryset, output_schema=model_view.output_schema
        )

    def test_list_model_ok(self):
        credentials: Credentials = self.get_credentials(self.test_case)
        instance: Model = self.get_instance(self.test_case)
        response = self.list_model(id=instance.pk, credentials=credentials.ok)
        self.assert_response_is_ok(response, id=instance.pk)

    def test_list_model_unauthorized(self):
        credentials: Credentials = self.get_credentials(self.test_case)
        if credentials.unauthorized is None:
            self.test_case.skipTest("No unauthorized credentials provided")
        instance: Model = self.get_instance(self.test_case)
        response = self.list_model(id=instance.pk, credentials=credentials.unauthorized)
        self.assert_response_is_bad_request(
            response, status_code=HTTPStatus.UNAUTHORIZED
        )

    def test_list_model_forbidden(self):
        credentials: Credentials = self.get_credentials(self.test_case)
        if credentials.forbidden is None:
            self.test_case.skipTest("No forbidden credentials provided")
        instance: Model = self.get_instance(self.test_case)
        response = self.list_model(id=instance.pk, credentials=credentials.forbidden)
        self.assert_response_is_bad_request(response, status_code=HTTPStatus.FORBIDDEN)
