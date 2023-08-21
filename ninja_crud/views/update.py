import copy
from http import HTTPStatus
from typing import Callable, List, Optional, Type, TypeVar

from django.db.models import Model
from django.http import HttpRequest
from ninja import Router, Schema

from ninja_crud.views import utils
from ninja_crud.views.abstract import AbstractModelView

# Type alias for a Django Model instance.
# It's a generic type that is bound to Django's base Model class,
# meaning it can represent any Django Model instance.
ModelType = TypeVar("ModelType", bound=Model)

# Type alias for a callable to be invoked before saving the updated instance.
# Should have the signature (request: HttpRequest, instance: Model, old_instance: Model) -> None.
PreSaveHook = Callable[[HttpRequest, ModelType, ModelType], None]

# Type alias for a callable to be invoked after saving the updated instance.
# Should have the signature (request: HttpRequest, instance: Model, old_instance: Model) -> None.
PostSaveHook = Callable[[HttpRequest, ModelType, ModelType], None]


class UpdateModelView(AbstractModelView):
    """
    A view class that handles updating a specific instance of a model.
    It allows customization through pre- and post-save hooks and also supports decorators.

    Example:
    ```python
    from ninja_crud.views import ModelViewSet, UpdateModelView
    from example.models import Department
    from example.schemas import DepartmentIn, DepartmentOut

    class DepartmentViewSet(ModelViewSet):
        model_class = Department

        # Usage: Update a department by id
        # PUT /departments/{id}/
        update = UpdateModelView(input_schema=DepartmentIn, output_schema=DepartmentOut)
    ```
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
        Initializes the UpdateModelView.

        Args:
            input_schema (Type[Schema]): The schema used to deserialize the payload.
            output_schema (Type[Schema]): The schema used to serialize the updated instance.
            pre_save (PreSaveHook, optional): A function that is called before saving the instance. Defaults to None.

                Should have the signature (request: HttpRequest, instance: Model, old_instance: Model) -> None.

                If not provided, the function will be a no-op.
            post_save (PostSaveHook, optional): A function that is called after saving the instance. Defaults to None.

                Should have the signature (request: HttpRequest, instance: Model, old_instance: Model) -> None.

                If not provided, the function will be a no-op.
            decorators (List[Callable], optional): A list of decorators to apply to the view. Defaults to None.
            router_kwargs (Optional[dict], optional): Additional arguments to pass to the router. Defaults to None.
        """

        super().__init__(decorators=decorators, router_kwargs=router_kwargs)
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.pre_save = pre_save
        self.post_save = post_save
        self.http_method = "PUT"

    def register_route(self, router: Router, model_class: Type[Model]) -> None:
        input_schema = self.input_schema
        output_schema = self.output_schema

        @router.api_operation(
            methods=[self.http_method],
            path=self.get_path(),
            response={HTTPStatus.OK: output_schema},
            operation_id=f"update_{utils.to_snake_case(model_class.__name__)}",
            summary=f"Update {model_class.__name__}",
            **self.router_kwargs,
        )
        @utils.merge_decorators(self.decorators)
        def update_model(
            request: HttpRequest,
            id: utils.get_id_type(model_class),
            payload: input_schema,
        ):
            instance = model_class.objects.get(pk=id)

            old_instance = None
            if self.pre_save is not None or self.post_save is not None:
                old_instance = copy.deepcopy(instance)

            for field, value in payload.dict(exclude_unset=True).items():
                setattr(instance, field, value)

            if self.pre_save is not None:
                self.pre_save(request, instance, old_instance)

            instance.full_clean()
            instance.save()

            if self.post_save is not None:
                self.post_save(request, instance, old_instance)

            return HTTPStatus.OK, instance

    def get_path(self) -> str:
        return "/{id}"
