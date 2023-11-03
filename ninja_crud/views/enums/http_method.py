from enum import Enum


class HTTPMethod(str, Enum):
    """HTTP request methods and their descriptions.

    See https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods for more information.
    """

    def __new__(cls, value, description=""):
        obj = str.__new__(cls)
        obj._value_ = value

        obj.description = description
        return obj

    GET = "GET", "Retrieve a resource"
    POST = "POST", "Create a resource"
    PUT = "PUT", "Update a resource"
    DELETE = "DELETE", "Delete a resource"
    PATCH = "PATCH", "Partially update a resource"
    HEAD = "HEAD", "Retrieve resource headers"
    OPTIONS = "OPTIONS", "Retrieve resource options"
