from typing import Any, Callable

Decorator = Callable[[Callable[..., Any]], Callable[..., Any]]
