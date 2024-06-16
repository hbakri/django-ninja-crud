from typing import Any, Dict, Optional, Type, cast

import ninja.orm.fields
import ninja.signature.utils
import pydantic
from django.db import models


class PathParametersTypeResolver:
    """
    Helper class for automatically resolving the type of path parameters in a URL
    based on a Django model class.

    This class utilizes the `ninja.orm.fields.get_schema_field` method to map Django
    model fields to their corresponding Python types, allowing the creation of a
    Pydantic model representing the path parameters.

    The `resolve` method takes a URL path and a Django model class as input and
    returns a dynamically generated Pydantic model representing the path parameters.
    If there are no path parameters in the given URL, it returns `None`.

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
        The `PathParametersTypeResolver` now relies on the
        `ninja.orm.fields.get_schema_field` method to determine the appropriate type
        for each path parameter based on the corresponding model field.
        This method supports a wide range of field types, including:
        - `models.AutoField`, `models.BigAutoField` -> `int`
        - `models.BigIntegerField`, `models.IntegerField`,
            `models.PositiveBigIntegerField`, `models.PositiveIntegerField`,
            `models.PositiveSmallIntegerField`, `models.SmallIntegerField` -> `int`
        - `models.BinaryField` -> `bytes`
        - `models.BooleanField`, `models.NullBooleanField` -> `bool`
        - `models.CharField`, `models.SlugField`, `models.TextField`, `models.FileField`,
            `models.FilePathField` -> `str`
        - `models.DateField` -> `datetime.date`
        - `models.DateTimeField` -> `datetime.datetime`
        - `models.DecimalField` -> `Decimal`
        - `models.DurationField` -> `datetime.timedelta`
        - `models.FloatField` -> `float`
        - `models.GenericIPAddressField`, `models.IPAddressField` -> `IPvAnyAddress`
        - `models.JSONField` -> `AnyObject`
        - `models.TimeField` -> `datetime.time`
        - `models.UUIDField` -> `UUID`

        Additionally, some PostgreSQL-specific fields are supported:
        - `models.ArrayField` -> `List`
        - `models.CICharField`, `models.CIEmailField`, `models.CITextField` -> `str`
        - `models.HStoreField` -> `Dict`

        For `models.ForeignKey` fields, the primary key type of the related model is
        used, and you can use both the real field name (e.g., `/{department_id}`) or
        the related model name (e.g., `/{department}`) in the path.

    Important:
        While `ninja.orm.fields.get_schema_field` supports a wide range of field types,
        it is not recommended to use all of them in URL paths. Path parameters should
        typically be limited to simple types like strings, integers, and UUIDs to ensure
        proper URL formatting and compatibility with web standards. Including complex
        types or fields with special characters in the URL path is generally discouraged.
    """

    @classmethod
    def resolve(
        cls, path: str, model_class: Type[models.Model]
    ) -> Optional[Type[pydantic.BaseModel]]:
        path_parameters_names = ninja.signature.utils.get_path_param_names(path)
        if not path_parameters_names:
            return None

        field_definitions: Dict[str, Any] = {
            path_parameter_name: ninja.orm.fields.get_schema_field(
                field=model_class._meta.get_field(field_name=path_parameter_name),
            )
            for path_parameter_name in path_parameters_names
        }
        return cast(
            Type[pydantic.BaseModel],
            pydantic.create_model("PathParametersType", **field_definitions),
        )
