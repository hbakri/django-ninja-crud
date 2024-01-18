from typing import Any, Type, Union, get_args, get_origin


class ViewValidator:
    @classmethod
    def validate(cls, attr_name: str, attr_value: Any, expected_type: Type) -> None:
        origin = get_origin(expected_type)

        if origin is None:
            cls._validate_instance(attr_name, attr_value, expected_type)

        elif origin is Union:
            cls._validate_union(attr_name, attr_value, expected_type)

        elif origin is type:
            cls._validate_type(attr_name, attr_value, expected_type)

        else:
            raise ValueError(
                f"Expected 'expected_type' to be a type, a Union, or None, but found "
                f"{origin}."
            )

    @staticmethod
    def _validate_instance(
        attr_name: str, attr_value: Any, expected_type: Type
    ) -> None:
        if not isinstance(attr_value, expected_type):
            raise TypeError(
                f"Expected '{attr_name}' to be an instance of "
                f"{expected_type.__name__}, but found type {type(attr_value)}."
            )

    @classmethod
    def _validate_union(
        cls, attr_name: str, attr_value: Any, expected_type: Type
    ) -> None:
        for arg in get_args(expected_type):
            try:
                cls.validate(attr_name, attr_value, arg)
                return
            except ValueError:
                pass

        raise ValueError(
            f"Attribute '{attr_name}' with value {attr_value} does not match any "
            f"type in Union {expected_type}."
        )

    @classmethod
    def _validate_type(
        cls, attr_name: str, attr_value: Any, expected_type: Type
    ) -> None:
        args = get_args(expected_type)
        if len(args) != 1:
            raise ValueError(
                f"Expected 'expected_type' to be a generic type with a single "
                f"type argument, but found {len(args)} type arguments: "
                f"{', '.join(args)}."
            )

        expected_type_arg = args[0]
        origin = get_origin(expected_type)
        if origin is None:
            if not isinstance(attr_value, type) or not issubclass(
                attr_value, expected_type_arg
            ):
                raise TypeError(
                    f"Expected '{attr_name}' to be a subclass of "
                    f"{expected_type_arg.__name__}, but found type {type(attr_value)}."
                )

        elif origin is list:
            ...
