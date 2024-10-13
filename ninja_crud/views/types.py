from typing import Any, Awaitable, Callable, Optional

from django.db.models import Model
from django.http import HttpRequest
from pydantic import BaseModel

Decorator = Callable[[Callable[..., Any]], Callable[..., Any]]

GetModel = Callable[[HttpRequest, Optional[BaseModel]], Model]
AsyncGetModel = Callable[[HttpRequest, Optional[BaseModel]], Awaitable[Model]]

ModelHook = Callable[[HttpRequest, Model], None]
AsyncModelHook = Callable[[HttpRequest, Model], Awaitable[None]]
