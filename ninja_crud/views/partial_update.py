from typing import Callable, List, Optional, Type

from ninja import Schema

from ninja_crud.views.update import PostSaveHook, PreSaveHook, UpdateModelView


class PartialUpdateModelView(UpdateModelView):
    """
    A view class that handles partially updating a specific instance of a model.

    This class extends UpdateModelView to support partial updates. All fields in the input schema are made optional,
    allowing clients to submit only the fields they want to update.

    Attributes are inherited from UpdateModelView, and the behavior of methods is the same except as noted below.

    Attributes:
        http_method (str): The HTTP method used for this view, defaulting to "PATCH".
            This is an internal attribute and not intended to be modified directly.
    """

    def __init__(
        self,
        input_schema: Type[Schema],
        output_schema: Type[Schema],
        pre_save: PreSaveHook = None,
        post_save: PostSaveHook = None,
        decorators: List[Callable] = None,
        router_kwargs: Optional[dict] = None,
    ) -> None:
        """
        Initializes the PartialUpdateModelView with the specified schemas, decorators, and hooks.

        All fields in the input schema are made optional, allowing clients to submit only the fields they want to update.

        Args:
            input_schema (Type[Schema]): The schema for validating the input data for the partial update.
            output_schema (Type[Schema]): The schema for serializing the updated instance.
            pre_save (PreSaveHook, optional): A callable to be invoked before saving the updated instance. Should be a
                function with the signature (request: HttpRequest, instance: Model, old_instance: Model) -> None.
            post_save (PostSaveHook, optional): A callable to be invoked after saving the updated instance. Should be a
                function with the signature (request: HttpRequest, instance: Model, old_instance: Model) -> None.
            decorators (List[Callable], optional): A list of decorators to apply to the view function.
            router_kwargs (Optional[dict], optional): A dictionary of keyword arguments to pass to the router.
        """

        super().__init__(
            input_schema=self.generate_partial_schema(input_schema),
            output_schema=output_schema,
            decorators=decorators,
            pre_save=pre_save,
            post_save=post_save,
            router_kwargs=router_kwargs,
        )
        self.http_method = "PATCH"

    @staticmethod
    def generate_partial_schema(schema_class: Type[Schema]) -> Type[Schema]:
        """
        Creates a new schema class based on the given schema_class, with all fields set as optional.

        Args:
            schema_class (Type[Schema]): The original schema class.

        Returns:
            Type[Schema]: A new schema class with all fields made optional.
        """

        class PartialSchema(schema_class):
            pass

        for field in PartialSchema.__fields__.values():
            field.required = False

        PartialSchema.__name__ = f"Partial{schema_class.__name__}"
        return PartialSchema
