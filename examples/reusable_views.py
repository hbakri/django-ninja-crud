from typing import Any, Optional
from uuid import UUID

from django.db import models
from django.http import HttpRequest
from ninja.constants import NOT_SET

from ninja_crud.views import APIView


class ReusableReadView(APIView):
    def __init__(
        self, response_schema: Any = NOT_SET, model: Optional[type[models.Model]] = None
    ) -> None:
        super().__init__(["GET"], "/{id}/reusable", response_schema=response_schema)
        self.model = model

    def endpoint(self, request: HttpRequest, id: UUID) -> models.Model:
        return self.model.objects.get(id=id)


class ReusableAsyncReadView(APIView):
    def __init__(
        self, response_schema: Any = NOT_SET, model: Optional[type[models.Model]] = None
    ) -> None:
        super().__init__(
            ["GET"], "/{id}/reusable/async", response_schema=response_schema
        )
        self.model = model

    async def endpoint(self, request: HttpRequest, id: UUID) -> models.Model:
        return await self.model.objects.aget(id=id)
