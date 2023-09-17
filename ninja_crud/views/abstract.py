import logging
from abc import ABC, abstractmethod
from typing import Callable, List, Optional, Type

from django.db.models import Model
from ninja import Router

logger = logging.getLogger(__name__)


class AbstractModelView(ABC):
    """
    An abstract base class for all model views.

    Subclasses must implement the register_route and get_path methods.
    """

    def __init__(
        self, decorators: List[Callable] = None, router_kwargs: Optional[dict] = None
    ) -> None:
        """
        Initializes the AbstractModelView with the given decorators and optional router keyword arguments.

        Args:
            decorators (List[Callable], optional): A list of decorators to apply to the view. Defaults to None.
            router_kwargs (dict, optional): Additional arguments to pass to the router. Defaults to None.
        """

        if decorators is None:
            decorators = []
        self.decorators = decorators
        self.router_kwargs = router_kwargs or {}

    @abstractmethod
    def register_route(
        self, router: Router, model_class: Type[Model]
    ) -> None:  # pragma: no cover
        """
        Abstract method to register the view's route with the given router and model class.

        Args:
            router (Router): The router to register the route with.
            model_class (Type[Model]): The Django model class for which the route should be created.

        Raises:
            NotImplementedError: This method must be implemented by a subclass.
        """
        pass

    @abstractmethod
    def get_path(self) -> str:  # pragma: no cover
        """
        Returns the URL path for this view, used in routing.

        Returns:
            str: The URL path.

        Raises:
            NotImplementedError: This method must be implemented by a subclass.
        """
        pass

    @staticmethod
    def _sanitize_and_merge_router_kwargs(
        default_router_kwargs: dict, custom_router_kwargs: dict
    ) -> dict:
        locked_keys = ["path", "response"]
        router_kwargs = custom_router_kwargs.copy()
        for key in locked_keys:
            if key in router_kwargs:
                logger.warning(f"Cannot override '{key}' in 'router_kwargs'.")
                router_kwargs.pop(key)

        return {**default_router_kwargs, **router_kwargs}
