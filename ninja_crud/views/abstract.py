from abc import ABC, abstractmethod
from typing import Callable, List, Optional, Type

from django.db.models import Model
from ninja import Router


class AbstractModelView(ABC):
    """
    Abstract class for a model view.

    Attributes:
        decorators (List[Callable], optional): A list of decorators to apply to the view function.
        router_kwargs (Optional[dict], optional): A dictionary of keyword arguments to pass to the router.
    """

    def __init__(
        self, decorators: List[Callable] = None, router_kwargs: Optional[dict] = None
    ) -> None:
        """
        Initializes the AbstractModelView with the given decorators and optional router keyword arguments.

        Args:
            decorators (List[Callable], optional): A list of decorators to apply to the view function.
            router_kwargs (Optional[dict], optional): A dictionary of keyword arguments to pass to the router.
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
