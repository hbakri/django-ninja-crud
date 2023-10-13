import datetime
import json
import uuid
from typing import List, Optional, Type, Union

from django.db.models import Model, QuerySet
from django.test import TestCase
from ninja import Schema
from ninja.pagination import PaginationBase


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
        content: Union[dict, List[dict]],
        queryset: QuerySet[Model],
        schema_class: Type[Schema],
        limit: int,
        offset: int,
        pagination_class: Optional[Type[PaginationBase]],
    ):
        if pagination_class is not None:
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

        else:
            test_case.assertIsInstance(content, list)
            test_case.assertEqual(len(content), queryset.count())

            for item in content:
                TestAssertionHelper.assert_content_equals_schema(
                    test_case, item, queryset, schema_class
                )
