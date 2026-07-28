from typing import Any, Optional, Union

import django.db.models
import ninja.constants
import pydantic

from ninja_crud import views
from ninja_crud.viewsets import APIViewSet


class CRUDViewSet(APIViewSet):
    def __init__(
        self,
        path_prefix: Optional[str] = None,
        model: Optional[type[django.db.models.Model]] = None,
        model_name: Optional[str] = None,
        model_plural_name: Optional[str] = None,
        body_schema: Optional[type[pydantic.BaseModel]] = None,
        query_schema: Optional[
            type[pydantic.BaseModel]
        ] = None,  # TODO: Add query_schema, with inheritance
        response_schema: Any = ninja.constants.NOT_SET,
    ):
        self.path_prefix = path_prefix or ""
        self.model = model
        self.model_name = model_name or model.__name__
        self.model_plural_name = model_plural_name or f"{self.model_name}s"
        self.body_schema = body_schema
        self.response_schema = response_schema

        self.list_view = views.ListView(path=f"{self.path_prefix}/")
        self.create_view = views.CreateView(path=f"{self.path_prefix}/")
        self.read_view = views.ReadView(path=f"{self.path_prefix}/{{id}}")
        self.update_view = views.UpdateView(path=f"{self.path_prefix}/{{id}}")
        self.delete_view = views.DeleteView(path=f"{self.path_prefix}/{{id}}")

    def register(self, router: Union[ninja.NinjaAPI, ninja.Router]) -> None:
        self._inherit_parent_attributes()
        self._validate_attributes()
        self._build_operation_names()
        super().register(router)

    def _inherit_parent_attributes(self) -> None:
        if self.parent:
            self.model = self.model or getattr(self.parent, "model", None)
            self.body_schema = self.body_schema or getattr(
                self.parent, "body_schema", None
            )
            self.response_schema = self.response_schema or getattr(
                self.parent, "response_schema", ninja.constants.NOT_SET
            )

    def _validate_attributes(self) -> None:
        if not self.model:
            raise ValueError(
                f"Model required for viewset {self.__class__.__name__}. "
                f"Set 'model' on the viewset or its parent."
            )

    def _build_operation_names(self) -> None:
        self.list_view.operation_name = f"list_{self.model_plural_name}"
        self.create_view.operation_name = f"create_{self.model_name}"
        self.read_view.operation_name = f"read_{self.model_name}"
        self.update_view.operation_name = f"update_{self.model_name}"
        self.delete_view.operation_name = f"delete_{self.model_name}"
