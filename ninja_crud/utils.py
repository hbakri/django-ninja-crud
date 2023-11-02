from typing import Type, get_args, get_origin


def validate_class_attribute_type(
    cls: Type, attr_name: str, expected_type: Type, optional: bool = False
) -> None:
    """
    Validates that a class attribute is of the expected type or is a subclass of the expected type.

    Args:
        cls (Type): The class whose attribute should be validated.
        attr_name (str): The name of the attribute to validate.
        expected_type (Type): The type that the attribute is expected to be or be a subclass of.
        optional (bool, optional): Whether the attribute is optional. If set to True, the attribute is allowed to be
                                   None or not present. Defaults to False.

    Raises:
        - ValueError: If the attribute is not optional and is not set.
        - TypeError: If the attribute value is not of the expected type or a subclass of the expected type.

    Example:
        >>> class ExampleClass:
        ...     attribute = dict()
        ...
        >>> validate_class_attribute_type(ExampleClass, 'attribute', dict)
        >>> validate_class_attribute_type(ExampleClass, 'non_existent_attribute', dict, optional=True)
        >>> validate_class_attribute_type(ExampleClass, 'attribute', str)  # Raises ValueError
    """
    attr_value = getattr(cls, attr_name, None)
    if attr_value is None:
        if not optional:
            raise ValueError(f"{cls.__name__}.{attr_name} class attribute must be set")
        else:
            return

    origin_expected_type = get_origin(expected_type)
    if origin_expected_type is not None:
        if origin_expected_type is type:
            # If expected_type is a generic type (e.g., Type[Model])
            type_arg = get_args(expected_type)[0]
            if not isinstance(attr_value, type) or not issubclass(attr_value, type_arg):
                raise TypeError(
                    f"{cls.__name__}.{attr_name} must be a subclass of {type_arg.__name__}"
                )
        else:  # pragma: no cover
            raise NotImplementedError(
                f"Handling for generic type {origin_expected_type} is not implemented"
            )
    else:
        # If expected_type is a regular type (e.g., int, str)
        if not isinstance(attr_value, expected_type):
            raise TypeError(
                f"{cls.__name__}.{attr_name} must be of type {expected_type.__name__}"
            )
