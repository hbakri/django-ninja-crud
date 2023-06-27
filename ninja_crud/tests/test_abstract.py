import inspect
import json
from http import HTTPStatus
from typing import Callable, List, NamedTuple, Optional, Tuple, Type, TypeVar, Union

from django.db.models import Model, QuerySet
from django.http import HttpResponse
from django.test import Client, TestCase
from ninja import Schema

from ninja_crud.tests.utils import default_serializer
from ninja_crud.views import (
    AbstractModelView,
    CreateModelView,
    ListModelView,
    ModelViewSet,
)

T = TypeVar("T")
TestCaseType = TypeVar("TestCaseType", bound=TestCase)
ParamsOrCallable = Union[T, Callable[[TestCaseType], T]]


class PathParams(NamedTuple):
    ok: dict
    not_found: Optional[dict] = None


class QueryParams(NamedTuple):
    ok: dict
    bad_request: Optional[dict] = None


class AuthParams(NamedTuple):
    ok: dict
    forbidden: Optional[dict] = None
    unauthorized: Optional[dict] = None


class BodyParams(NamedTuple):
    ok: dict
    bad_request: Optional[dict] = None
    conflict: Optional[dict] = None


class AbstractModelViewTest:
    model_view_set: ModelViewSet
    test_case: TestCase
    client: Client
    model_view: Type[AbstractModelView]
    name: str

    def __init__(
        self,
        path_params: ParamsOrCallable[PathParams, TestCaseType],
        auth_params: ParamsOrCallable[AuthParams, TestCaseType] = None,
    ) -> None:
        self.path_params = path_params
        self.auth_params = auth_params

    def get_path_params(self) -> PathParams:
        if callable(self.path_params):
            return self.path_params(self.test_case)
        return self.path_params

    def get_auth_params(self) -> AuthParams:
        if self.auth_params is None:
            return AuthParams(ok={})
        elif callable(self.auth_params):
            return self.auth_params(self.test_case)
        return self.auth_params

    def get_tests(self) -> List[Tuple[str, Callable]]:
        return [
            (name, method)
            for name, method in inspect.getmembers(self, predicate=inspect.ismethod)
            if name.startswith("test")
        ]

    def get_model_view(self):
        for attr_name in dir(self.model_view_set):
            attr_value = getattr(self.model_view_set, attr_name)
            if (
                isinstance(attr_value, self.model_view)
                and self.name == f"test_{attr_name}"
            ):
                return attr_value

    def assert_content_equals_schema(
        self, content: dict, queryset: QuerySet[Model], output_schema: Type[Schema]
    ):
        self.test_case.assertIsInstance(content, dict)

        self.test_case.assertIn("id", content)
        self.test_case.assertTrue(queryset.filter(id=content["id"]).exists())
        self.test_case.assertEqual(queryset.filter(id=content["id"]).count(), 1)

        element = queryset.get(id=content["id"])
        self.assert_dict_equals_schema(content, output_schema.from_orm(element))

    def assert_dict_equals_schema(self, element: dict, schema: Schema):
        copied_element = {}
        for key, value in element.items():
            copied_element[key] = value

        self.test_case.assertDictEqual(
            copied_element,
            json.loads(json.dumps(schema.dict(), default=default_serializer)),
        )

    def assert_content_equals_schema_list(
        self,
        content: List[dict],
        queryset: QuerySet[Model],
        output_schema: Type[Schema],
        limit: int,
        offset: int,
    ):
        self.test_case.assertIsInstance(content, dict)

        self.test_case.assertIn("count", content)
        count = content["count"]
        self.test_case.assertIsInstance(count, int)
        self.test_case.assertEqual(count, queryset.count())

        self.test_case.assertIn("items", content)
        items = content["items"]
        self.test_case.assertIsInstance(items, list)

        queryset_items = queryset[offset : offset + limit]
        self.test_case.assertEqual(len(items), queryset_items.count())

        for item in items:
            self.assert_content_equals_schema(item, queryset, output_schema)

    def assert_response_is_bad_request(
        self, response: HttpResponse, status_code: HTTPStatus
    ):
        self.test_case.assertEqual(response.status_code, status_code)
        content = json.loads(response.content)
        self.test_case.assertIsInstance(content, dict)
        self.test_case.assertIn("detail", content)


class ModelViewSetTestMeta(type):
    model_view_set: ModelViewSet
    client_class: callable

    def __new__(mcs, name, bases, dct):
        new_cls = super().__new__(mcs, name, bases, dct)
        test_case = new_cls()
        for attr_name in dir(new_cls):
            attr_value = getattr(new_cls, attr_name)
            if isinstance(attr_value, AbstractModelViewTest):
                attr_value.model_view_set = new_cls.model_view_set
                attr_value.test_case = test_case
                attr_value.client = new_cls.client_class()
                attr_value.name = attr_name
                for test_name, test_func in attr_value.get_tests():
                    method = attr_value.get_model_view()
                    model_name = new_cls.model_view_set.model.__name__.lower()
                    substring_replace = model_name
                    if isinstance(method, (ListModelView, CreateModelView)):
                        if method.detail:
                            related_model_name = method.related_model.__name__.lower()
                            substring_replace = f"{model_name}_{related_model_name}"
                    new_test_name = test_name.replace("model", substring_replace)
                    setattr(new_cls, new_test_name, test_func)
        return new_cls


class ModelViewSetTest(metaclass=ModelViewSetTestMeta):
    model_view_set: ModelViewSet
