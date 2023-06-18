from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, List, Type

from django.db.models import Model
from ninja import Router


class AbstractModelView(ABC):
    def __init__(self, decorators: List[Callable] = None) -> None:
        if decorators is None:
            decorators = []
        self.decorators = decorators

    @abstractmethod
    def register_route(
        self, router: Router, model: Type[Model]
    ) -> None:  # pragma: no cover
        pass


class ModelViewSet:
    model: Type[Model]

    @classmethod
    def register_routes(cls, router: Router) -> None:
        for attr_name in dir(cls):
            attr_value = getattr(cls, attr_name)
            if isinstance(attr_value, AbstractModelView):
                attr_value.register_route(router, cls.model)
