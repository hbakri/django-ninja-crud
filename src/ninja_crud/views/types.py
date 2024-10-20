from collections.abc import Awaitable
from typing import Any, Callable, Optional

from django.db.models import Model, QuerySet
from django.http import HttpRequest
from pydantic import BaseModel

Decorator = Callable[[Callable[..., Any]], Callable[..., Any]]

ModelHook = Callable[[HttpRequest, Model], None]
AsyncModelHook = Callable[[HttpRequest, Model], Awaitable[None]]

ModelGetter = Callable[[HttpRequest, Optional[BaseModel]], Model]
AsyncModelGetter = Callable[[HttpRequest, Optional[BaseModel]], Awaitable[Model]]

QuerySetGetter = Callable[[HttpRequest, Optional[BaseModel]], QuerySet[Model]]
AsyncQuerySetGetter = Callable[
    [HttpRequest, Optional[BaseModel]], Awaitable[QuerySet[Model]]
]
QuerySetFilter = Callable[[QuerySet[Model], Optional[BaseModel]], QuerySet[Model]]
