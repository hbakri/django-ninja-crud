import asyncio
import functools
from typing import Any, Callable, Optional, Union, get_args, get_origin

import django.db.models
import ninja.orm.fields
import ninja.signature.utils
import pydantic


def to_function(obj: Callable[..., Any]) -> Callable[..., Any]:
    """
    Converts a callable into a standalone operation function compatible with Django
    Ninja. Preserves the original synchronous or asynchronous behavior.
    """

    @functools.wraps(obj)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        return await obj(*args, **kwargs)

    @functools.wraps(obj)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        return obj(*args, **kwargs)

    return async_wrapper if asyncio.iscoroutinefunction(obj) else sync_wrapper


def build_path_schema(
    path: str, model: type[django.db.models.Model]
) -> Optional[type[pydantic.BaseModel]]:
    """
    Resolve path parameters to a pydantic model based on the path structure and
    associated Django model.

    Designed for subclasses of APIView, this method enables dynamic path schema
    handling without explicit type specification. It supports any paths, like
    "/{name}", "/{id}", or "/{related_model_id}", or even complex paths like
    "/{related_model_id}/models/{id}", automatically resolving types from model
    fields.

    This feature *significantly* reduces boilerplate code and allows for easy
    creation of reusable views with varied path structures, especially useful when
    refactoring repetitive endpoints into an APIView subclass.

    Utilizes Django Ninja utilities to extract and map path parameters to model
    fields. Returns `None` if no parameters are found in the path.

    Args:
        path (str): The URL path.
        model (type[django.db.models.Model] | None): The associated Django model.

    Returns:
        type[pydantic.BaseModel] | None: A generated Pydantic model class for path
            parameters, or None if no parameters exist in the path.

    Example:
        For path `"/{department_id}/employees/{id}"` and `Employee` model:

        ```python
        class PathParameters(pydantic.BaseModel):
            department_id: UUID
            id: UUID
        ```

    Notes:
        - Supports various Django field types (e.g., AutoField, CharField,
            DateField, UUIDField).
        - For ForeignKey, uses the primary key type of the related model.
        - Supports both real field names (e.g., /{department_id}) and related
            model names (e.g., /{department}).

    Important:
        Prefer simple types (strings, integers, UUIDs) for path parameters to
        ensure proper URL formatting and web standard compatibility.
    """
    path_parameters_names = ninja.signature.utils.get_path_param_names(path)
    if not path_parameters_names:
        return None

    schema_fields: dict[str, Any] = {}
    for field_name in path_parameters_names:
        field = model._meta.get_field(field_name)
        field_type, _ = ninja.orm.fields.get_schema_field(field=field)
        schema_fields[field_name] = (
            get_args(field_type)[0] if get_origin(field_type) is Union else field_type,
            ...,
        )

    return pydantic.create_model("PathSchema", **schema_fields)
