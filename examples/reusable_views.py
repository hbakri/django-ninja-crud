from typing import Optional, Type
from uuid import UUID

import django.http
import pydantic
from django.db import models

from ninja_crud.views import APIView


class ReusableReadView(APIView):
    def __init__(
        self,
        name: Optional[str] = None,
        model: Optional[Type[models.Model]] = None,
        response_body: Optional[Type[pydantic.BaseModel]] = None,
    ) -> None:
        super().__init__(
            name=name,
            methods=["GET"],
            path="/{id}/reusable",
            response_status=200,
            response_body=response_body,
            model=model,
        )

    def handler(self, request: django.http.HttpRequest, id: UUID) -> models.Model:
        return self.model.objects.get(id=id)
