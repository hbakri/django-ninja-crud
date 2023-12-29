from typing import List, Optional

from ninja_crud.views.enums import HTTPMethod


class HTTPMethodValidator:
    @classmethod
    def validate(
        cls, method: HTTPMethod, choices: Optional[List[HTTPMethod]] = None
    ) -> None:
        if not isinstance(method, HTTPMethod):
            raise TypeError(
                f"Expected 'method' to be an instance of {HTTPMethod.__name__}, but found type {type(method)}."
            )

        if choices is not None and method not in choices:
            raise ValueError(
                f"Expected 'method' to be one of {choices}, but found {method}."
            )
