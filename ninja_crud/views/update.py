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

    Attributes:
        input_schema (Type[Schema]): The schema used to validate the input data.
        output_schema (Type[Schema]): The schema used to serialize the updated instance.
        pre_save (PreSaveHook, optional): A callable to be invoked before saving the updated instance. Should be a
            function with the signature (request: HttpRequest, instance: Model, old_instance: Model) -> None.
        post_save (PostSaveHook, optional): A callable to be invoked after saving the updated instance. Should be a
            function with the signature (request: HttpRequest, instance: Model, old_instance: Model) -> None.
        decorators (List[Callable], optional): A list of decorators to apply to the view function.
        router_kwargs (Optional[dict], optional): A dictionary of keyword arguments to pass to the router.
        http_method (str): The HTTP method used for this view, defaulting to "PUT". This is an internal attribute and
            not intended to be modified directly.
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
        Initializes the UpdateModelView with the specified schemas, decorators, and hooks.

        Args:
            input_schema (Type[Schema]): The schema for validating the input data for the update.
            output_schema (Type[Schema]): The schema for serializing the updated instance.
            pre_save (PreSaveHook, optional): A callable to be invoked before saving the updated instance. Should be a
                function with the signature (request: HttpRequest, instance: Model, old_instance: Model) -> None.
            post_save (PostSaveHook, optional): A callable to be invoked after saving the updated instance. Should be a
                function with the signature (request: HttpRequest, instance: Model, old_instance: Model) -> None.
            decorators (List[Callable], optional): A list of decorators to apply to the view function.
            router_kwargs (Optional[dict], optional): A dictionary of keyword arguments to pass to the router.
        """

        super().__init__(decorators=decorators, router_kwargs=router_kwargs)
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.pre_save = pre_save
        self.post_save = post_save
        self.http_method = "PUT"

    def register_route(self, router: Router, model_class: Type[Model]) -> None:
        """
        Registers the update route for the given model class.

        Args:
            router (Router): The Ninja router to register the route with.
            model_class (Type[Model]): The Django model class for the update view.

        Note:
            This method is usually called by the parent class and should not be called manually.
        """

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
        """
        Returns the URL path for this view, used in routing.

        Returns:
            str: The URL path.
        """
        return "/{id}"
