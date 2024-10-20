from collections.abc import Awaitable
from typing import Any, Callable

from django.db.models import Model, QuerySet
from django.http import HttpRequest
from pydantic import BaseModel

Decorator = Callable[[Callable[..., Any]], Callable[..., Any]]

ModelHook = Callable[[HttpRequest, Model], None]
AsyncModelHook = Callable[[HttpRequest, Model], Awaitable[None]]

ModelGetter = Callable[[HttpRequest, BaseModel | None], Model]
AsyncModelGetter = Callable[[HttpRequest, BaseModel | None], Awaitable[Model]]

QuerySetGetter = Callable[[HttpRequest, BaseModel | None], QuerySet[Model]]
AsyncQuerySetGetter = Callable[
    [HttpRequest, BaseModel | None], Awaitable[QuerySet[Model]]
]
QuerySetFilter = Callable[[QuerySet[Model], BaseModel | None], QuerySet[Model]]
