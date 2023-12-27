from typing import Type
from uuid import UUID

from django.db.models import Model


def merge_decorators(decorators):
    def merged_decorator(func):
        for decorator in reversed(decorators):
            func = decorator(func)
        return func

    return merged_decorator


def get_id_type(model_class: Type[Model]) -> Type:  # pragma: no cover
    id_field = model_class._meta.pk
    id_internal_type = id_field.get_internal_type()

    if id_internal_type == "UUIDField":
        id_type = UUID
    elif id_internal_type in [
        "SmallAutoField",
        "AutoField",
        "BigAutoField",
        "SmallIntegerField",
        "IntegerField",
        "BigIntegerField",
    ]:
        id_type = int
    elif id_internal_type in ["CharField", "SlugField"]:
        id_type = str
    elif id_internal_type == "BinaryField":
        id_type = bytes
    else:
        raise NotImplementedError(
            f"id_internal_type {id_internal_type} not implemented"
        )

    return id_type
