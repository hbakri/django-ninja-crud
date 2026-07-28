from typing import ClassVar, Optional, Union

import ninja

from ninja_crud.views import APIView


class APIViewSet:
    """
    Groups related API views and handles their registration in Django Ninja.

    APIViewSet provides a declarative way to define and organize related API views.
    Views can be defined as class attributes and are automatically registered with
    the specified router. The viewset supports nested viewsets, inheritance of
    attributes from parent viewsets, and flexible view configuration.

    Class Attributes:
        router (Union[ninja.NinjaAPI, ninja.Router], optional): Router for view
            registration. Views register automatically if provided.
        parent (APIViewSet, optional): Parent viewset for attribute inheritance.
    """

    router: ClassVar[Optional[Union[ninja.NinjaAPI, ninja.Router]]] = None
    parent: Optional["APIViewSet"] = None

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        if cls.router:
            cls().register(cls.router)

    def register(self, router: Union[ninja.NinjaAPI, ninja.Router]) -> None:
        for name, attribute in (vars(self.__class__) | vars(self)).items():
            if isinstance(attribute, APIView):
                attribute.operation_name = attribute.operation_name or name
                attribute.parent = self
                attribute.register(router)
            elif isinstance(attribute, APIViewSet) and name != "parent":
                attribute.parent = self
                attribute.register(router)
