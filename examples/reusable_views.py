from typing import Optional, Type
from uuid import UUID

import pydantic
from django.db import models
from django.http import HttpRequest

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
        )
        self.model = model

    def handler(self, request: HttpRequest, id: UUID) -> models.Model:
        return self.model.objects.get(id=id)


class ReusableAsyncReadView(APIView):
    def __init__(
        self,
        name: Optional[str] = None,
        model: Optional[Type[models.Model]] = None,
        response_body: Optional[Type[pydantic.BaseModel]] = None,
    ) -> None:
        super().__init__(
            name=name,
            methods=["GET"],
            path="/{id}/reusable/async",
            response_status=200,
            response_body=response_body,
        )
        self.model = model

    async def handler(self, request: HttpRequest, id: UUID) -> models.Model:
        return await self.model.objects.aget(id=id)
