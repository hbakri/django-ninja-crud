from typing import Callable, List, Optional, Type

from ninja import Schema

from ninja_crud.views.update import PostSaveHook, PreSaveHook, UpdateModelView


class PatchModelView(UpdateModelView):
    """
    A view class that handles partially updating a specific instance of a model.

    This class extends UpdateModelView to support partial updates. All fields in the input schema are made optional,
    allowing clients to submit only the fields they want to update.

    Attributes are inherited from UpdateModelView, and the behavior of methods is the same except as noted below.

    Attributes:
        http_method (str): The HTTP method used for this view, defaulting to "PATCH". This is an internal attribute and not intended to be modified directly.
    """

    def __init__(
        self,
        input_schema: Type[Schema],
        output_schema: Type[Schema],
        decorators: List[Callable] = None,
        pre_save: PreSaveHook = None,
        post_save: PostSaveHook = None,
        router_kwargs: Optional[dict] = None,
    ) -> None:
        """
        Initializes the PatchModelView with the specified schemas, decorators, and hooks.

        All fields in the input schema are made optional, allowing clients to submit only the fields they want to update.

        Args:
            input_schema (Type[Schema]): The schema to validate the input data.
            output_schema (Type[Schema]): The schema to serialize the updated object.
            decorators (List[Callable], optional): A list of decorators to apply to the view function.
            pre_save (PreSaveHook, optional): A hook to call before saving the updated object. Should have the signature (request: HttpRequest, instance: ModelType, old_instance: ModelType) -> None.
            post_save (PostSaveHook, optional): A hook to call after saving the updated object. Should have the signature (request: HttpRequest, instance: ModelType, old_instance: ModelType) -> None.
            router_kwargs (Optional[dict], optional): A dictionary of keyword arguments to pass to the router.
        """

        optional_input_schema = self.generate_optional_schema(input_schema)
        super().__init__(
            input_schema=optional_input_schema,
            output_schema=output_schema,
            decorators=decorators,
            pre_save=pre_save,
            post_save=post_save,
            router_kwargs=router_kwargs,
        )
        self.http_method = "PATCH"

    @staticmethod
    def generate_optional_schema(schema_class: Type[Schema]) -> Type[Schema]:
        """
        Creates a new schema class based on the given schema_class, with all fields set as optional.

        Args:
            schema_class (Type[Schema]): The original schema class.

        Returns:
            Type[Schema]: A new schema class with all fields made optional.
        """

        class OptionalSchema(schema_class):
            ...

        for field in OptionalSchema.__fields__.values():
            field.required = False

        OptionalSchema.__name__ = f"Optional{schema_class.__name__}"
        return OptionalSchema
