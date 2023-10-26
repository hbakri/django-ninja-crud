from typing import Any, Callable, Type


def iterate_class_attributes(cls: Type, func: Callable[[str, Any], None]):
    """
    Iterates over all attributes of a class and its ancestors in method resolution order (MRO),
    and applies a provided function to each attribute. Each attribute is processed only once,
    even if it is defined in multiple ancestors.

    The provided function should take two parameters: the name of the attribute and the attribute itself.

    Args:
        cls (Type): The class whose attributes should be iterated over.
        func (Callable[[str, Any], None]): The function to apply to each attribute. The function should
                                            accept two parameters: the name of the attribute (str) and the
                                            attribute itself (Any).

    Example:
        >>> class A:
        ...     x = 1
        ...     y = 2
        ...
        >>> class B(A):
        ...     z = 3
        ...     y = 4
        ...
        >>> def print_attr(name, attr):
        ...     print(name, attr)
        ...
        >>> iterate_class_attributes(B, print_attr)
        z 3
        y 4
        x 1
    """
    processed_attr_names = set()
    for base_cls in cls.__mro__:
        for attr_name, attr_value in vars(base_cls).items():
            if attr_name in processed_attr_names:
                continue
            func(attr_name, attr_value)
            processed_attr_names.add(attr_name)


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
        ValueError: If the attribute is not present (and 'optional' is False), or if the attribute value is not
                    of the expected type.

    Example:
        >>> class ExampleClass:
        ...     attribute = dict
        ...
        >>> validate_class_attribute_type(ExampleClass, 'attribute', dict)
        >>> validate_class_attribute_type(ExampleClass, 'non_existent_attribute', dict, optional=True)
        >>> validate_class_attribute_type(ExampleClass, 'attribute', str)  # Raises ValueError
    """
    attr_value = getattr(cls, attr_name, None)
    if attr_value is None and not optional:
        raise ValueError(f"{cls.__name__}.{attr_name} class attribute must be set")
    elif not isinstance(attr_value, type) or not issubclass(attr_value, expected_type):
        raise ValueError(
            f"{cls.__name__}.{attr_name} must be a subclass of {expected_type.__name__}"
        )
