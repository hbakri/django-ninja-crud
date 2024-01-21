from inspect import signature
from types import MappingProxyType
from typing import Callable, Optional

from django.db.models import QuerySet


class QuerySetGetterValidator:
    @classmethod
    def validate(
        cls, queryset_getter: Optional[Callable[..., QuerySet]], path: str
    ) -> None:
        if queryset_getter is None:
            return

        if not callable(queryset_getter):
            raise TypeError(
                f"Expected 'queryset_getter' to be callable, but found type {type(queryset_getter)}."
            )

        parameters = signature(queryset_getter).parameters
        if "{id}" in path:
            cls._validate_detail(parameters=parameters)
        else:
            cls._validate_collection(parameters=parameters)

    @staticmethod
    def _validate_detail(parameters: MappingProxyType) -> None:
        if len(parameters) != 1:
            raise ValueError(
                f"Expected 'queryset_getter' to accept a single 'id' parameter when path contains '{{id}}'. "
                f"Instead, found {len(parameters)} parameters: {', '.join(parameters)}."
            )

    @staticmethod
    def _validate_collection(parameters: MappingProxyType) -> None:
        if len(parameters) != 0:
            raise ValueError(
                f"Expected 'queryset_getter' to accept no parameters when path does not contain '{{id}}'. "
                f"Instead, found {len(parameters)} parameters: {', '.join(parameters)}."
            )
