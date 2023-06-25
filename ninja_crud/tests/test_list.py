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
from ninja_crud.views.list import ListModelView


class ListModelViewTest(AbstractModelViewTest):
    model_view = ListModelView

    def __init__(
        self,
        instance_getter: Callable[[TestCase], Model],
        credentials_getter: Callable[[TestCase], Credentials] = None,
        filters: Payloads = None,
    ) -> None:
        super().__init__(
            instance_getter=instance_getter, credentials_getter=credentials_getter
        )
        self.filters = filters

    def list_model(
        self, id: Union[int, UUID], credentials: dict, data: dict = None
    ) -> HttpResponse:
        model_view: ListModelView = self.get_model_view()
        model_name = utils.to_snake_case(self.model_view_set.model.__name__)
        if model_view.detail:
            related_model_name = utils.to_snake_case(model_view.related_model.__name__)
            url_name = f"{model_name}_{related_model_name}s"
            kwargs = {"id": id}
        else:
            url_name = f"{model_name}s"
            kwargs = {}

        response = self.client.get(
            reverse(f"api:{url_name}", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **credentials,
        )
        return response

    def assert_response_is_ok(
        self, response: HttpResponse, id: Union[int, UUID], data: dict = None
    ):
        self.test_case.assertEqual(response.status_code, HTTPStatus.OK)
        content = json.loads(response.content)

        model_view: ListModelView = self.get_model_view()

        if model_view.detail:
            if model_view.get_queryset is not None:
                queryset = model_view.get_queryset(id)
            else:
                queryset = model_view.related_model.objects.get_queryset()
        else:
            if model_view.get_queryset is not None:
                queryset = model_view.get_queryset()
            else:
                queryset = self.model_view_set.model.objects.get_queryset()

        if data is not None:
            limit = data.pop("limit", 100)
            offset = data.pop("offset", 0)
            filter_instance = model_view.filter_schema(**data)
            queryset = model_view.filter_queryset(queryset, filter_instance)
        else:
            limit = 100
            offset = 0

        self.assert_content_equals_schema_list(
            content,
            queryset=queryset,
            output_schema=model_view.output_schema,
            limit=limit,
            offset=offset,
        )

    def test_list_model_ok(self):
        credentials: Credentials = self.get_credentials(self.test_case)
        instance: Model = self.get_instance(self.test_case)
        response = self.list_model(id=instance.pk, credentials=credentials.ok)
        self.assert_response_is_ok(response, id=instance.pk)

        if self.filters is not None:
            with self.test_case.subTest(data=self.filters.ok):
                response = self.list_model(
                    id=instance.pk, credentials=credentials.ok, data=self.filters.ok
                )
                self.assert_response_is_ok(
                    response, id=instance.pk, data=self.filters.ok
                )

    def test_list_model_bad_request(self):
        if self.filters is None or self.filters.bad_request is None:
            self.test_case.skipTest("No bad request filters provided")
        credentials: Credentials = self.get_credentials(self.test_case)
        instance: Model = self.get_instance(self.test_case)
        response = self.list_model(
            id=instance.pk,
            credentials=credentials.ok,
            data=self.filters.bad_request,
        )
        self.assert_response_is_bad_request(
            response, status_code=HTTPStatus.BAD_REQUEST
        )

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
