from inspect import signature
from types import MappingProxyType
from typing import Union

from django.db.models import Model

from ninja_crud.views.types import CollectionInstanceBuilder, DetailInstanceBuilder


class InstanceBuilderValidator:
    @staticmethod
    def validate(
        instance_builder: Union[DetailInstanceBuilder, CollectionInstanceBuilder],
        detail: bool,
    ) -> None:
        if instance_builder is None:
            return

        if not callable(instance_builder):
            raise TypeError(
                f"Expected 'instance_builder' to be callable, but found type {type(instance_builder)}."
            )

        parameters = signature(instance_builder).parameters
        if detail:
            InstanceBuilderValidator._validate_for_detail(instance_builder, parameters)
        else:
            InstanceBuilderValidator._validate_for_collection(
                instance_builder, parameters
            )

    @staticmethod
    def _validate_for_detail(
        instance_builder: DetailInstanceBuilder, parameters: MappingProxyType
    ) -> None:
        if len(parameters) != 1:
            raise ValueError(
                f"Expected 'instance_builder' to accept a single 'id' parameter when 'detail=True'. "
                f"Instead, found {len(parameters)} parameters: {', '.join(parameters)}."
            )
        InstanceBuilderValidator._check_model_type(instance=instance_builder(None))

    @staticmethod
    def _validate_for_collection(
        instance_builder: CollectionInstanceBuilder, parameters: MappingProxyType
    ) -> None:
        if len(parameters) != 0:
            raise ValueError(
                f"Expected 'instance_builder' to accept no parameters when 'detail=False'. "
                f"Instead, found {len(parameters)} parameters: {', '.join(parameters)}."
            )
        InstanceBuilderValidator._check_model_type(instance=instance_builder())

    @staticmethod
    def _check_model_type(instance: Model) -> None:
        if not isinstance(instance, Model):
            raise TypeError(
                f"Expected 'instance_builder' to return an instance of a Django Model, but found type {type(instance)}."
            )
