---
title: Setup
excerpt: How to set up Django Ninja CRUD
category: 655765078baf1c0308327480
---

To set up Django Ninja CRUD in your project, you will need to make some additions to your `api.py` file. Below is a complete example of what your `api.py` file might look like after adding the package.

```python
from http import HTTPStatus

from django.core.exceptions import (
    FieldError,
    ObjectDoesNotExist,
    PermissionDenied,
    ValidationError,
)
from ninja import NinjaAPI
from ninja.errors import ValidationError as NinjaValidationError

api = NinjaAPI(urls_namespace="api")

# api.add_router(...)

@api.exception_handler(ObjectDoesNotExist)
def handle_object_does_not_exist(request, exc):
    return api.create_response(
        request,
        {"message": "ObjectDoesNotExist", "detail": str(exc)},
        status=HTTPStatus.NOT_FOUND,
    )

@api.exception_handler(PermissionDenied)
def handle_permission_error(request, exc: PermissionDenied):
    return api.create_response(
        request,
        {
            "message": "PermissionDenied",
            "detail": "You don't have the permission to access this resource.",
        },
        status=HTTPStatus.FORBIDDEN,
    )

@api.exception_handler(NinjaValidationError)
def handle_ninja_validation_error(request, exc: NinjaValidationError):
    mapped_msg = {error["loc"][-1]: error["msg"] for error in exc.errors}
    return api.create_response(
        request,
        data={"message": "NinjaValidationError", "detail": mapped_msg},
        status=HTTPStatus.BAD_REQUEST,
    )

@api.exception_handler(ValidationError)
def handle_validation_error(request, exc: ValidationError):
    status = HTTPStatus.BAD_REQUEST
    for field, errors in exc.error_dict.items():
        for error in errors:
            if error.code in ["unique", "unique_together"]:
                status = HTTPStatus.CONFLICT
    return api.create_response(
        request,
        data={"message": "ValidationError", "detail": exc.message_dict},
        status=status,
    )

@api.exception_handler(FieldError)
def handle_field_error(request, exc: FieldError):
    return api.create_response(
        request,
        data={"message": "FieldError", "detail": str(exc)},
        status=HTTPStatus.BAD_REQUEST,
    )

```

The setup for `django-ninja-crud` primarily involves setting up the exception handlers correctly. This is a vital step as it ensures that when an error occurs during the processing of requests, an appropriate HTTP response is sent back to the client. It's also a generally accepted best practice when setting up API endpoints.

In the provided code, we have four exception handlers:

- `ObjectDoesNotExist`: Handles cases where the requested object does not exist in the database.
- `PermissionDenied`: Handles cases where the client does not have the necessary permissions to access a resource.
- `ValidationError`: Handles cases where there's an error during the validation of a Django model instance.
- `NinjaValidationError`: Handles cases where the data sent by the client fails validation checks.

These handlers cover a wide range of potential issues and should be included in the setup of your Django Ninja project, regardless of whether or not you're using the `django-ninja-crud` package.

In conclusion, the setup for `django-ninja-crud` is minimal and primarily involves the correct configuration of exception handlers. Depending on your specific needs, you may need to add exception handlers, but the provided setup offers a solid foundation.
