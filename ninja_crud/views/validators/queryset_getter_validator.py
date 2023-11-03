from inspect import signature
from types import MappingProxyType
from typing import Union

from django.db.models import Model, QuerySet

from ninja_crud.views.helpers.types import (
    CollectionQuerySetGetter,
    DetailQuerySetGetter,
)


class QuerySetGetterValidator:
    @staticmethod
    def validate(
        queryset_getter: Union[DetailQuerySetGetter, CollectionQuerySetGetter],
        detail: bool,
    ) -> None:
        if queryset_getter is None:
            return

        if not callable(queryset_getter):
            raise TypeError(
                f"Expected 'queryset_getter' to be callable, but found type {type(queryset_getter)}."
            )

        parameters = signature(queryset_getter).parameters
        if detail:
            QuerySetGetterValidator._validate_for_detail(parameters, queryset_getter)
        else:
            QuerySetGetterValidator._validate_for_collection(
                parameters, queryset_getter
            )

    @staticmethod
    def _validate_for_detail(
        parameters: MappingProxyType,
        queryset_getter: DetailQuerySetGetter,
    ) -> None:
        if len(parameters) != 1:
            raise ValueError(
                f"Expected 'queryset_getter' to accept a single 'id' parameter when 'detail=True'. "
                f"Instead, found {len(parameters)} parameters: {', '.join(parameters)}."
            )
        QuerySetGetterValidator._check_queryset_type(queryset=queryset_getter(None))

    @staticmethod
    def _validate_for_collection(
        parameters: MappingProxyType,
        queryset_getter: CollectionQuerySetGetter,
    ) -> None:
        if len(parameters) != 0:
            raise ValueError(
                f"Expected 'queryset_getter' to accept no parameters when 'detail=False'. "
                f"Instead, found {len(parameters)} parameters: {', '.join(parameters)}."
            )
        QuerySetGetterValidator._check_queryset_type(queryset=queryset_getter())

    @staticmethod
    def _check_queryset_type(queryset: QuerySet[Model]):
        if not isinstance(queryset, QuerySet):
            raise TypeError(
                f"Expected 'queryset_getter' to return a QuerySet when 'detail=True', but found type {type(queryset)}."
            )
