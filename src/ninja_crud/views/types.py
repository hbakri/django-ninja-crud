from collections.abc import Awaitable
from typing import Any, Callable

from django.db.models import Model, QuerySet
from django.http import HttpRequest
from pydantic import BaseModel

Decorator = Callable[[Callable[..., Any]], Callable[..., Any]]

ModelHook = Callable[[HttpRequest, Model], None]
AsyncModelHook = Callable[[HttpRequest, Model], Awaitable[None]]

PathParameters = BaseModel | None
QueryParameters = BaseModel | None

ModelGetter = Callable[[HttpRequest, PathParameters], Model]
AsyncModelGetter = Callable[[HttpRequest, PathParameters], Awaitable[Model]]

QuerySetGetter = Callable[[HttpRequest, PathParameters], QuerySet[Model]]
QuerySetFilter = Callable[[QuerySet[Model], QueryParameters], QuerySet[Model]]
AsyncQuerySetGetter = Callable[
    [HttpRequest, PathParameters], Awaitable[QuerySet[Model]]
]
