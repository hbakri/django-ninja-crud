from typing import Optional, Type

import django.http
import pydantic
from django.db import models

from ninja_crud.views import APIView


class ReusableReadView(APIView):
    def __init__(
        self,
        model: Optional[Type[models.Model]] = None,
        response_body: Optional[Type[pydantic.BaseModel]] = None,
    ) -> None:
        super().__init__(
            method="GET",
            path="/{id}",
            response_status=200,
            response_body=response_body,
            view_function=self._view_function,
            model=model,
        )

    def _view_function(
        self,
        request: django.http.HttpRequest,
        path_parameters: Optional[pydantic.BaseModel],
        query_parameters: Optional[pydantic.BaseModel],
        request_body: Optional[pydantic.BaseModel],
    ) -> models.Model:
        return self.model.objects.get(id=path_parameters.id)
