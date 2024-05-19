import re
import uuid
from typing import Any, Dict, Optional, Set, Type, cast

import pydantic
from django.db import models


class PathParametersTypeResolver:
    """
    Helper class for resolving the type of path parameters based on a model class
    and URL path variables.

    This class maps Django model field types to corresponding Python types, allowing
    automatic determination of path parameter types in API views.

    The `resolve` method takes a URL path and a Django model class, and returns a
    Pydantic model representing the path parameters. If there are no path parameters,
    it returns `None`.

    Attributes:
        field_type_mapping (Dict[Type[models.Field], Type]): A mapping of Django model
            field types to their corresponding Python types for Pydantic models.

    Example:
    ```python
    from uuid import UUID
    from ninja_crud.views.helpers import PathParametersTypeResolver
    from examples.models import Department, Employee

    # Simple example with a single path parameter:
    path = "/{name}"
    model_class = Department
    path_parameters_type = PathParametersTypeResolver.resolve(path, model_class)

    # Will create a Pydantic model with a single field "name" of type str, e.g.:
    # class PathParametersType(pydantic.BaseModel):
    #     name: str

    # Now a more complex example with multiple path parameters and a ForeignKey:
    path = "/{department_id}/employees/{id}"
    model_class = Employee
    path_parameters_type = PathParametersTypeResolver.resolve(path, model_class)

    # Will create this Pydantic model:
    # class PathParametersType(pydantic.BaseModel):
    #     department_id: UUID
    #     id: UUID
    ```

    Note:
        Supported field type mappings are as follows:
        - `models.AutoField`, `models.SmallAutoField`, `models.BigAutoField` -> `int`
        - `models.IntegerField`, `models.SmallIntegerField`, `models.BigIntegerField`,
            `models.PositiveIntegerField`, `models.PositiveSmallIntegerField`,
            `models.PositiveBigIntegerField` -> `int`
        - `models.UUIDField` -> `uuid.UUID`
        - `models.CharField`, `models.SlugField`, `models.TextField` -> `str`
        - `models.BinaryField` -> `bytes`
        - `models.ForeignKey` -> Primary key type of the related model, but only if
            the real field name is used in the path (e.g., `/{department_id}` instead
            of `/{department}`). If the related model is `"self"`, the primary key of
            the current model is used.
        - Other field types are not supported and will raise a `ValueError`.
    """

    field_type_mapping = {
        models.AutoField: int,
        models.SmallAutoField: int,
        models.BigAutoField: int,
        models.IntegerField: int,
        models.SmallIntegerField: int,
        models.BigIntegerField: int,
        models.PositiveIntegerField: int,
        models.PositiveSmallIntegerField: int,
        models.PositiveBigIntegerField: int,
        models.UUIDField: uuid.UUID,
        models.CharField: str,
        models.SlugField: str,
        models.TextField: str,
        models.BinaryField: bytes,
    }

    @classmethod
    def resolve(
        cls, path: str, model_class: Type[models.Model]
    ) -> Optional[Type[pydantic.BaseModel]]:
        path_parameters_names: Set[str] = {
            item.strip("{}").split(":")[-1] for item in re.findall("{[^}]*}", path)
        }
        if not path_parameters_names:
            return None

        field_definitions: Dict[str, Any] = {
            path_parameter_name: (
                cls._resolve_field_type(
                    model_class=model_class,
                    field_name=path_parameter_name,
                ),
                ...,
            )
            for path_parameter_name in path_parameters_names
        }
        return cast(
            Type[pydantic.BaseModel],
            pydantic.create_model("PathParametersType", **field_definitions),
        )

    @classmethod
    def _resolve_field_type(
        cls, model_class: Type[models.Model], field_name: str
    ) -> Type[Any]:
        field = model_class._meta.get_field(field_name)

        if isinstance(field, models.ForeignKey) and field_name == field.attname:
            related_model_class = (
                field.related_model if field.related_model != "self" else model_class
            )
            related_model_pk_field = related_model_class._meta.pk
            if related_model_pk_field is not None:
                return cls._resolve_field_type(
                    model_class=related_model_class,
                    field_name=related_model_pk_field.name,
                )

        field_type = cls.field_type_mapping.get(type(field))
        if field_type is None:
            raise ValueError(
                f"Field {field_name} of model {model_class.__name__} has an "
                f"unsupported type: {type(field)}."
            )

        return field_type
