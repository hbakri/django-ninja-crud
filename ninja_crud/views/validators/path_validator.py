import re


class PathValidator:
    @staticmethod
    def validate(path: str, detail: bool) -> None:
        if not isinstance(path, str):
            raise TypeError(
                f"Expected 'path' to be a string, but found type {type(path)}."
            )

        if not path.startswith("/"):
            raise ValueError(
                f"Expected 'path' to start with a forward slash ('/'), but found '{path}'."
            )

        if detail:
            PathValidator._validate_for_detail(path)
        else:
            PathValidator._validate_for_collection(path)

    @staticmethod
    def _validate_for_detail(path: str) -> None:
        pattern = re.compile(r"^/?[^{]*(\{id})[^{]*$")
        if not pattern.match(path):
            raise ValueError(
                f"Detail route path must contain only one parameter, and that should be {{id}}, got '{path}'"
            )

    @staticmethod
    def _validate_for_collection(path: str) -> None:
        pattern = re.compile(r"^/?[^{]*$")
        if not pattern.match(path):
            raise ValueError(
                f"Collection route path must not contain any parameters, got '{path}'"
            )
