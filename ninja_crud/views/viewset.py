from __future__ import annotations

from typing import Type

from django.db.models import Model
from ninja import Router

from ninja_crud.views import AbstractModelView


class ModelViewSetMeta(type):
    @staticmethod
    def validate_model_class(
        new_cls: ModelViewSetMeta,
    ):  # pragma: no cover
        cls_attr_name = "model_class"
        if not hasattr(new_cls, cls_attr_name):
            raise ValueError(
                f"{new_cls.__name__}.{cls_attr_name} class attribute must be set"
            )
        cls_attr_value = getattr(new_cls, cls_attr_name)
        if not isinstance(cls_attr_value, type) or not issubclass(
            cls_attr_value, Model
        ):
            raise ValueError(
                f"{new_cls.__name__}.{cls_attr_name} must be a subclass of django.db.models.Model"
            )

    def __new__(mcs, name, bases, attrs):
        new_cls = super().__new__(mcs, name, bases, attrs)

        if name != "ModelViewSet":
            mcs.validate_model_class(new_cls)

        return new_cls


class ModelViewSet(metaclass=ModelViewSetMeta):
    model_class: Type[Model]

    @classmethod
    def register_routes(cls, router: Router) -> None:
        for attr_name in dir(cls):
            attr_value = getattr(cls, attr_name)
            if isinstance(attr_value, AbstractModelView):
                attr_value.register_route(router, cls.model_class)
