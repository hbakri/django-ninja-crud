import datetime
import json
import uuid
from http import HTTPStatus
from typing import List, Type

from django.db.models import Model, QuerySet
from django.http import HttpResponse
from django.test import TestCase
from ninja import Schema


def default_serializer(obj):
    if isinstance(obj, uuid.UUID):
        return str(obj)
    elif isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    else:  # pragma: no cover
        raise TypeError(f"Type {type(obj)} not serializable")


class TestAssertionHelper:
    @staticmethod
    def assert_content_equals_schema(
        test_case: TestCase,
        content: dict,
        queryset: QuerySet[Model],
        schema_class: Type[Schema],
    ):
        test_case.assertIsInstance(content, dict)

        test_case.assertIn("id", content)
        test_case.assertTrue(queryset.filter(pk=content["id"]).exists())
        test_case.assertEqual(queryset.filter(pk=content["id"]).count(), 1)

        model = queryset.get(pk=content["id"])
        schema = schema_class.from_orm(model)
        test_case.assertDictEqual(
            content,
            json.loads(json.dumps(schema.dict(), default=default_serializer)),
        )

    @staticmethod
    def assert_content_equals_schema_list(
        test_case: TestCase,
        content: List[dict],
        queryset: QuerySet[Model],
        schema_class: Type[Schema],
        limit: int,
        offset: int,
    ):
        test_case.assertIsInstance(content, dict)

        test_case.assertIn("count", content)
        count = content["count"]
        test_case.assertIsInstance(count, int)
        test_case.assertEqual(count, queryset.count())

        test_case.assertIn("items", content)
        items = content["items"]
        test_case.assertIsInstance(items, list)

        queryset_items = queryset[offset : offset + limit]
        test_case.assertEqual(len(items), queryset_items.count())

        for item in items:
            TestAssertionHelper.assert_content_equals_schema(
                test_case, item, queryset, schema_class
            )

    @staticmethod
    def assert_response_is_bad_request(
        test_case: TestCase, response: HttpResponse, status_code: HTTPStatus
    ):
        test_case.assertEqual(response.status_code, status_code)
        content = json.loads(response.content)
        test_case.assertIsInstance(content, dict)
        test_case.assertIn("detail", content)
