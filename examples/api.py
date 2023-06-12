from http import HTTPStatus

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
from ninja import NinjaAPI
from ninja.errors import ValidationError as NinjaValidationError
from ninja.security import HttpBearer

from examples.views.view_department import router as department_router
from examples.views.view_employee import router as employee_router


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        if token == "supersecret":
            return token


api = NinjaAPI(urls_namespace="api", auth=AuthBearer())
api.add_router("departments", department_router, tags=["departments"])
api.add_router("employees", employee_router, tags=["employees"])


@api.exception_handler(ObjectDoesNotExist)
def _(request, exc):
    return api.create_response(
        request,
        {"message": "Object not found", "detail": str(exc)},
        status=HTTPStatus.NOT_FOUND,
    )


@api.exception_handler(PermissionDenied)
def _(request, exc: PermissionDenied):
    return api.create_response(
        request,
        {
            "message": "PermissionDenied",
            "detail": "You don't have the permission to access this resource.",
        },
        status=HTTPStatus.FORBIDDEN,
    )


@api.exception_handler(NinjaValidationError)
def _(request, exc: NinjaValidationError):
    mapped_msg = {error["loc"][-1]: error["msg"] for error in exc.errors}
    return api.create_response(
        request,
        data={"message": "ValidationError", "detail": mapped_msg},
        status=HTTPStatus.BAD_REQUEST,
    )


@api.exception_handler(ValidationError)
def _(request, exc: ValidationError):
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
