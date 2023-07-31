from abc import ABC, abstractmethod
from typing import Callable, List, Type, Optional

from django.db.models import Model
from ninja import Router


class AbstractModelView(ABC):
    def __init__(self, decorators: List[Callable] = None, router_kwargs: Optional[dict] = None) -> None:
        if decorators is None:
            decorators = []
        self.decorators = decorators
        self.router_kwargs = router_kwargs or {}

    @abstractmethod
    def register_route(
        self, router: Router, model_class: Type[Model]
    ) -> None:  # pragma: no cover
        pass

    @abstractmethod
    def get_path(self) -> str:  # pragma: no cover
        pass
