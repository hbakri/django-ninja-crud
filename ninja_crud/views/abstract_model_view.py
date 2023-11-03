import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable, List, Optional, Type

from django.db.models import Model
from ninja import Router

from ninja_crud.views.enums import HTTPMethod
from ninja_crud.views.validators.path_validator import PathValidator

if TYPE_CHECKING:  # pragma: no cover
    from ninja_crud.viewsets import ModelViewSet

logger = logging.getLogger(__name__)


class AbstractModelView(ABC):
    """
    An abstract base class for all model views.

    Subclasses must implement the register_route method.
    """

    def __init__(
        self,
        method: HTTPMethod,
        path: str,
        detail: bool,
        decorators: Optional[List[Callable]] = None,
        router_kwargs: Optional[dict] = None,
    ) -> None:
        """
        Initializes the AbstractModelView with the given decorators and optional router keyword arguments.

        Args:
            method (HTTPMethod): The HTTP method for the view.
            path (str): The path to use for the view.
            detail (bool): Whether the view is for a detail or collection route.
            decorators (Optional[List[Callable]], optional): A list of decorators to apply to the view. Defaults to [].
            router_kwargs (Optional[dict], optional): Additional arguments to pass to the router. Defaults to {}.
        """
        if not isinstance(method, HTTPMethod):
            raise TypeError(
                f"Expected 'method' to be an instance of HTTPMethod, but found type {type(method)}."
            )
        self.method = method
        PathValidator.validate(path, detail)
        self.path = path
        self.detail = detail
        self.decorators = decorators or []
        self.router_kwargs = router_kwargs or {}
        self.viewset_class: Optional[Type["ModelViewSet"]] = None

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

    @staticmethod
    def _sanitize_and_merge_router_kwargs(
        default_router_kwargs: dict, custom_router_kwargs: dict
    ) -> dict:
        locked_keys = ["path", "response"]
        router_kwargs = custom_router_kwargs.copy()
        for locked_key in locked_keys:
            if locked_key in router_kwargs:
                logger.warning(f"Cannot override '{locked_key}' in 'router_kwargs'.")
                router_kwargs.pop(locked_key)

        return {**default_router_kwargs, **router_kwargs}

    def bind_to_viewset(
        self, viewset_class: Type["ModelViewSet"], model_view_name: str
    ) -> None:
        self.viewset_class = viewset_class

    def bind_default_value(
        self,
        viewset_class: Type["ModelViewSet"],
        model_view_name: str,
        attribute_name: str,
        default_attribute_name: str,
    ):
        if getattr(self, attribute_name, None) is None:
            default_attribute = getattr(viewset_class, default_attribute_name, None)
            if default_attribute is None:
                raise ValueError(
                    f"Could not determine '{attribute_name}' for {viewset_class.__name__}.{model_view_name}."
                )
            setattr(self, attribute_name, default_attribute)
