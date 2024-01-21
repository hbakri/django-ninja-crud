from typing import Type
from uuid import UUID

from django.db.models import Model


def get_id_type(model_class: Type[Model]) -> Type:
    id_field = model_class._meta.pk
    id_internal_type = id_field.get_internal_type()

    type_mapping = {
        "UUIDField": UUID,
        "SmallAutoField": int,
        "AutoField": int,
        "BigAutoField": int,
        "SmallIntegerField": int,
        "IntegerField": int,
        "BigIntegerField": int,
        "CharField": str,
        "SlugField": str,
        "BinaryField": bytes,
    }

    id_type = type_mapping.get(id_internal_type)

    if id_type is None:  # pragma: no cover
        raise NotImplementedError(
            f"id_internal_type {id_internal_type} not implemented"
        )

    return id_type
