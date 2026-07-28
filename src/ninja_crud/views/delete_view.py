from typing import Annotated, Any, Optional, Union, cast

from django.db import models
from django.http import HttpRequest
from ninja import NinjaAPI, Router
from ninja.constants import NOT_SET
from ninja.params.functions import Path
from pydantic import BaseModel

from ninja_crud.views import utils
from ninja_crud.views.api_view import APIView
from ninja_crud.views.types import Decorator, ModelGetter, ModelHook


class DeleteView(APIView):
    def __init__(
        self,
        *,
        # Path configuration
        path: str = "/{id}",
        path_schema: Optional[type[BaseModel]] = None,
        methods: Optional[list[str]] = None,
        # Model configuration
        model: Optional[type[models.Model]] = None,
        get_model: Optional[ModelGetter] = None,
        # Operation hooks
        pre_delete: Optional[ModelHook] = None,
        post_delete: Optional[ModelHook] = None,
        # Response configuration
        response_schema: Any = NOT_SET,
        status_code: Optional[int] = None,
        responses: Optional[dict[int, Any]] = None,
        response_schema_by_alias: bool = False,
        response_schema_exclude_unset: bool = False,
        response_schema_exclude_defaults: bool = False,
        response_schema_exclude_none: bool = False,
        # Security and performance
        auth: Any = NOT_SET,
        throttle: Any = NOT_SET,
        decorators: Optional[list[Decorator]] = None,
        # URL configuration
        url_name: Optional[str] = None,
        # OpenAPI documentation
        operation_name: Optional[str] = None,
        operation_id: Optional[str] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[list[str]] = None,
        deprecated: Optional[bool] = None,
        include_in_schema: bool = True,
        openapi_extra: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            path=path,
            methods=methods or ["DELETE"],
            response_schema=response_schema,
            status_code=status_code,
            responses=responses,
            auth=auth,
            throttle=throttle,
            decorators=decorators,
            operation_name=operation_name,
            operation_id=operation_id,
            summary=summary,
            description=description,
            tags=tags,
            deprecated=deprecated,
            response_schema_by_alias=response_schema_by_alias,
            response_schema_exclude_unset=response_schema_exclude_unset,
            response_schema_exclude_defaults=response_schema_exclude_defaults,
            response_schema_exclude_none=response_schema_exclude_none,
            url_name=url_name,
            include_in_schema=include_in_schema,
            openapi_extra=openapi_extra,
        )
        self.model = model
        self.path_schema = path_schema
        self.get_model = get_model or (
            lambda request, path_parameters: cast(
                type[models.Model], self.model
            ).objects.get(**(path_parameters.model_dump() if self.path_schema else {}))
        )
        self.pre_delete = pre_delete or (lambda request, instance: None)
        self.post_delete = post_delete or (lambda request, instance: None)

    def endpoint(
        self,
        request: HttpRequest,
        path_parameters: Optional[BaseModel],
    ) -> None:
        instance = self.get_model(request, path_parameters)
        self.pre_delete(request, instance)
        instance.delete()
        self.post_delete(request, instance)

    def register(self, router: Union[NinjaAPI, Router]) -> None:
        self._inherit_parent_attributes()
        self._validate_attributes()
        self._build_path_schema()
        self._update_endpoint_type_hints()
        super().register(router)

    def _inherit_parent_attributes(self) -> None:
        if self.parent:
            self.model = self.model or getattr(self.parent, "model", None)

    def _validate_attributes(self) -> None:
        if not self.model:
            raise ValueError(
                f"Model required for view {self.__class__.__name__}. "
                f"Set 'model' on the view or its parent."
            )

    def _build_path_schema(self) -> None:
        if not self.path_schema:
            self.path_schema = utils.build_path_schema(self.path, self.model)

    def _update_endpoint_type_hints(self) -> None:
        self.endpoint.__annotations__["path_parameters"] = Annotated[
            self.path_schema, Path(default=None, include_in_schema=False)
        ]
