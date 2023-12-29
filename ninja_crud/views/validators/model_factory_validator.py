from inspect import signature
from types import MappingProxyType

from ninja_crud.views.helpers.types import ModelFactory


class ModelFactoryValidator:
    @classmethod
    def validate(cls, model_factory: ModelFactory, path: str) -> None:
        if model_factory is None:
            return

        if not callable(model_factory):
            raise TypeError(
                f"Expected 'model_factory' to be callable, but found type {type(model_factory)}."
            )

        parameters = signature(model_factory).parameters
        if "{id}" in path:
            cls._validate_detail(parameters)
        else:
            cls._validate_collection(parameters)

    @staticmethod
    def _validate_detail(parameters: MappingProxyType) -> None:
        if len(parameters) != 1:
            raise ValueError(
                f"Expected 'model_factory' to accept a single 'id' parameter when path contains '{{id}}'. "
                f"Instead, found {len(parameters)} parameters: {', '.join(parameters)}."
            )

    @staticmethod
    def _validate_collection(parameters: MappingProxyType) -> None:
        if len(parameters) != 0:
            raise ValueError(
                f"Expected 'model_factory' to accept no parameters when path does not contain '{{id}}'. "
                f"Instead, found {len(parameters)} parameters: {', '.join(parameters)}."
            )
