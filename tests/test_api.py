from http import HTTPStatus

from django.core.exceptions import (
    FieldError,
    ObjectDoesNotExist,
    PermissionDenied,
    ValidationError,
)
from ninja import NinjaAPI
from ninja.errors import ValidationError as NinjaValidationError

from examples.views.department_views import router as department_router
from examples.views.employee_views import router as employee_router
from tests.test_app.views.collection_views import router as collection_router
from tests.test_app.views.item_views import router as item_router
from tests.test_app.views.user_views import router as user_router
from tests.test_authentication import TokenBearer

api = NinjaAPI(urls_namespace="api")
api.add_router(
    "collections", collection_router, auth=TokenBearer(), tags=["collections"]
)
api.add_router("items", item_router, auth=TokenBearer(), tags=["items"])
api.add_router("users", user_router, tags=["users"])
api.add_router("departments", department_router, auth=None, tags=["departments"])
api.add_router("employees", employee_router, auth=None, tags=["employees"])


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
    for _, errors in exc.error_dict.items():
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
