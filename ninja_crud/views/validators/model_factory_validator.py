from inspect import signature
from types import MappingProxyType
from typing import Union

from django.db.models import Model

from ninja_crud.views.helpers.types import CollectionModelFactory, DetailModelFactory


class ModelFactoryValidator:
    @staticmethod
    def validate(
        model_factory: Union[DetailModelFactory, CollectionModelFactory],
        detail: bool,
    ) -> None:
        if model_factory is None:
            return

        if not callable(model_factory):
            raise TypeError(
                f"Expected 'model_factory' to be callable, but found type {type(model_factory)}."
            )

        parameters = signature(model_factory).parameters
        if detail:
            ModelFactoryValidator._validate_for_detail(model_factory, parameters)
        else:
            ModelFactoryValidator._validate_for_collection(model_factory, parameters)

    @staticmethod
    def _validate_for_detail(
        model_factory: DetailModelFactory, parameters: MappingProxyType
    ) -> None:
        if len(parameters) != 1:
            raise ValueError(
                f"Expected 'model_factory' to accept a single 'id' parameter when 'detail=True'. "
                f"Instead, found {len(parameters)} parameters: {', '.join(parameters)}."
            )
        ModelFactoryValidator._check_model_type(model=model_factory(None))

    @staticmethod
    def _validate_for_collection(
        model_factory: CollectionModelFactory, parameters: MappingProxyType
    ) -> None:
        if len(parameters) != 0:
            raise ValueError(
                f"Expected 'model_factory' to accept no parameters when 'detail=False'. "
                f"Instead, found {len(parameters)} parameters: {', '.join(parameters)}."
            )
        ModelFactoryValidator._check_model_type(model=model_factory())

    @staticmethod
    def _check_model_type(model: Model) -> None:
        if not isinstance(model, Model):
            raise TypeError(
                f"Expected 'model_factory' to return an instance of a Django Model, but found type {type(model)}."
            )
