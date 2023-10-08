from typing import Callable, List, Optional, Type

from ninja import Schema

from ninja_crud.views.types import UpdateSaveHook
from ninja_crud.views.update import UpdateModelView


class PartialUpdateModelView(UpdateModelView):
    """
    A view class that handles partially updating instances of a model.
    It allows customization through pre- and post-save hooks and also supports decorators.

    Example:
    ```python
    from ninja_crud.views import ModelViewSet, PartialUpdateModelView
    from example.models import Department
    from example.schemas import DepartmentIn, DepartmentOut

    class DepartmentViewSet(ModelViewSet):
        model_class = Department

        # Usage: Partially update a department by id
        # PATCH /departments/{id}/
        partial_update = PartialUpdateModelView(input_schema=DepartmentIn, output_schema=DepartmentOut)
    ```
    """

    def __init__(
        self,
        input_schema: Type[Schema],
        output_schema: Type[Schema],
        pre_save: Optional[UpdateSaveHook] = None,
        post_save: Optional[UpdateSaveHook] = None,
        path: Optional[str] = None,
        decorators: Optional[List[Callable]] = None,
        router_kwargs: Optional[dict] = None,
    ) -> None:
        """
        Initializes the PartialUpdateModelView.
        All fields in the input schema are made optional, allowing clients to submit only
        the fields they want to update.

        Args:
            input_schema (Type[Schema]): The schema used to deserialize the payload.
            output_schema (Type[Schema]): The schema used to serialize the updated instance.
            pre_save (UpdateSaveHook, optional): A function that is called before saving the instance. Defaults to None.

                The function should have the signature:
                - (request: HttpRequest, old_instance: Model, new_instance: Model) -> None

                If not provided, the function will be a no-op.
            post_save (UpdateSaveHook, optional): A function that is called after saving the instance. Defaults to None.

                The function should have the signature:
                - (request: HttpRequest, old_instance: Model, new_instance: Model) -> None

                If not provided, the function will be a no-op.
            path (str, optional): The path to use for the view. Defaults to "/{id}".
            decorators (List[Callable], optional): A list of decorators to apply to the view. Defaults to [].
            router_kwargs (dict, optional): Additional arguments to pass to the router. Defaults to {}.
        """

        super().__init__(
            input_schema=self._generate_partial_schema(input_schema),
            output_schema=output_schema,
            pre_save=pre_save,
            post_save=post_save,
            path=path,
            decorators=decorators,
            router_kwargs=router_kwargs,
        )
        self.http_method = "PATCH"

    @staticmethod
    def _generate_partial_schema(schema_class: Type[Schema]) -> Type[Schema]:
        class PartialSchema(schema_class):
            pass

        for field in PartialSchema.__fields__.values():
            field.required = False

        PartialSchema.__name__ = f"Partial{schema_class.__name__}"
        return PartialSchema
