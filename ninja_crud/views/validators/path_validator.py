import re


class PathValidator:
    @classmethod
    def validate(cls, path: str, allow_no_parameters: bool = True) -> None:
        if not isinstance(path, str):
            raise TypeError(
                f"Expected 'path' to be a string, but found type {type(path)}."
            )

        if not cls._is_path_valid(path, allow_no_parameters):
            expected = (
                "a path with no parameters or" if allow_no_parameters else "a path with"
            )
            raise ValueError(
                f"Invalid path '{path}'. Expected {expected} exactly one '{{id}}' parameter."
            )

    @classmethod
    def _is_path_valid(cls, path: str, allow_no_parameters: bool) -> bool:
        has_no_parameters = cls._has_no_parameters(path)
        has_only_id_parameter = cls._has_only_id_parameter(path)
        return has_only_id_parameter or (allow_no_parameters and has_no_parameters)

    @staticmethod
    def _has_no_parameters(path: str) -> bool:
        no_parameters_pattern = r"^[^{}]*$"
        return re.match(no_parameters_pattern, path) is not None

    @staticmethod
    def _has_only_id_parameter(path: str) -> bool:
        only_id_parameter_pattern = r"^[^{}]*\{id\}[^{}]*$"
        return re.match(only_id_parameter_pattern, path) is not None
