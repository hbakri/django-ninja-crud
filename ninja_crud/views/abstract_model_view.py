import abc
import http
import re
import uuid
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Type, Union

import ninja
import pydantic
from django.db.models import Field, ForeignKey, Model

from ninja_crud.views.abstract_view import AbstractView
from ninja_crud.views.enums import HTTPMethod

if TYPE_CHECKING:  # pragma: no cover
    from ninja_crud.viewsets import ModelViewSet


class AbstractModelView(AbstractView, abc.ABC):
    """
    An abstract view class that handles model operations.

    Args:
        method (HTTPMethod): View HTTP method.
        path (str): View path.
        path_parameters (Optional[Type[ninja.Schema]], optional): Schema for
            deserializing path parameters. Defaults to None.
        query_parameters (Optional[Type[ninja.Schema]], optional): Schema for
            deserializing query parameters. Defaults to None.
        request_body (Optional[Type[ninja.Schema]], optional): Schema for deserializing
            the request body. Defaults to None.
        response_body (Optional[Type[ninja.Schema]], optional): Schema for serializing
            the response body. Defaults to None.
        response_status (http.HTTPStatus, optional): HTTP status code for the response.
            Defaults to http.HTTPStatus.OK.
        decorators (Optional[List[Callable]], optional): Decorators for the view.
            Defaults to [].
        router_kwargs (Optional[Dict], optional): Additional router arguments, with
            overrides for 'path', 'methods', and 'response' being ignored. Defaults
            to {}.
    """

    def __init__(
        self,
        method: HTTPMethod,
        path: str,
        path_parameters: Optional[Type[ninja.Schema]] = None,
        query_parameters: Optional[Type[ninja.Schema]] = None,
        request_body: Optional[Type[ninja.Schema]] = None,
        response_body: Union[Type[ninja.Schema], Type[List[ninja.Schema]], None] = None,
        response_status: http.HTTPStatus = http.HTTPStatus.OK,
        decorators: Optional[List[Callable]] = None,
        router_kwargs: Optional[Dict] = None,
    ) -> None:
        super().__init__(
            method=method,
            path=path,
            path_parameters=path_parameters,
            query_parameters=query_parameters,
            request_body=request_body,
            response_body=response_body,
            response_status=response_status,
            decorators=decorators,
            router_kwargs=router_kwargs,
        )
        self._model_viewset_class: Optional[Type["ModelViewSet"]] = None

    @property
    def model_viewset_class(self) -> Type["ModelViewSet"]:
        if self._model_viewset_class is None:
            raise ValueError(
                f"Viewset class not bound to {self.__class__.__name__}. "
                "Please bind a viewset class before accessing this property."
            )
        return self._model_viewset_class

    @model_viewset_class.setter
    def model_viewset_class(self, model_viewset_class: Type["ModelViewSet"]) -> None:
        if self._model_viewset_class is not None:
            raise ValueError(
                f"{self.__class__.__name__} is already bound to a viewset."
            )
        self._model_viewset_class = model_viewset_class
        self._inherit_model_viewset_class_attributes()

        if not self.path_parameters:
            self._infer_path_parameters_schema_class()

    def _inherit_model_viewset_class_attributes(self) -> None:
        pass

    def _infer_path_parameters_schema_class(self):
        path_parameter_field_names = re.findall(r"{(\w+)}", self.path)
        if not path_parameter_field_names:
            return

        path_parameter_field_definitions = {
            path_parameter_field_name: (
                self._infer_field_type(
                    model_class=self.model_viewset_class.model,
                    field_name=path_parameter_field_name,
                ),
                ...,
            )
            for path_parameter_field_name in path_parameter_field_names
        }
        self.path_parameters = pydantic.create_model(
            __model_name="PathParametersSchema", **path_parameter_field_definitions
        )

    @classmethod
    def _infer_field_type(cls, model_class: Type[Model], field_name: str) -> Type:
        field: Field = model_class._meta.get_field(field_name)

        if isinstance(field, ForeignKey) and field_name == field.attname:
            related_model_class: Type[Model] = field.related_model
            return cls._infer_field_type(
                model_class=related_model_class,
                field_name=related_model_class._meta.pk.name,
            )

        type_mapping = {
            "AutoField": int,
            "SmallAutoField": int,
            "BigAutoField": int,
            "IntegerField": int,
            "SmallIntegerField": int,
            "BigIntegerField": int,
            "PositiveIntegerField": int,
            "PositiveSmallIntegerField": int,
            "PositiveBigIntegerField": int,
            "UUIDField": uuid.UUID,
            "CharField": str,
            "SlugField": str,
            "TextField": str,
            "BinaryField": bytes,
        }

        field_type = type_mapping.get(field.get_internal_type())
        if field_type is None:
            raise ValueError(
                f"Field {field_name} of model {model_class.__name__} has an "
                f"unsupported type: {field.get_internal_type()}."
            )

        return field_type
