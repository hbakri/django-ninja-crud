from typing import Type

from django.db.models import Model
from ninja import Router

from ninja_crud.views import AbstractModelView


class ModelViewSet:
    model_class: Type[Model]

    @classmethod
    def register_routes(cls, router: Router) -> None:
        for attr_name in dir(cls):
            attr_value = getattr(cls, attr_name)
            if isinstance(attr_value, AbstractModelView):
                attr_value.register_route(router, cls.model_class)
