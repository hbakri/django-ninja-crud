from typing import Callable, List, Type, Optional

from ninja import Schema

from ninja_crud.views.update import PostSaveHook, PreSaveHook, UpdateModelView


class PatchModelView(UpdateModelView):
    def __init__(
        self,
        input_schema: Type[Schema],
        output_schema: Type[Schema],
        decorators: List[Callable] = None,
        pre_save: PreSaveHook = None,
        post_save: PostSaveHook = None,
        router_kwargs: Optional[dict] = None,
    ) -> None:
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
        class OptionalSchema(schema_class):
            ...

        for field in OptionalSchema.__fields__.values():
            field.required = False

        OptionalSchema.__name__ = f"Optional{schema_class.__name__}"
        return OptionalSchema
