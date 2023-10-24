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
