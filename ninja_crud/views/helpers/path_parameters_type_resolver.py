from typing import Any, Dict, Optional, Type, cast

import ninja.orm.fields
import ninja.signature.utils
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
