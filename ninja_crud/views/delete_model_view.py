from http import HTTPStatus
from typing import Callable, Dict, List, Optional

from django.db.models import Model
from django.http import HttpRequest
from ninja import Schema

from ninja_crud.views.abstract_model_view import AbstractModelView
from ninja_crud.views.enums import HTTPMethod


class DeleteModelView(AbstractModelView):
    """
    A view class that handles deleting a model instance.

    Args:
        path (str, optional): View path. Defaults to "/{id}".
        path_parameters (Optional[Type[ninja.Schema]], optional): Schema for
            deserializing path parameters. Automatically inferred from the path
            and the fields of the `ModelViewSet`'s associated model if not provided.
            Defaults to None.
        get_model (Optional[Callable[[Optional[ninja.Schema]],
            django.db.models.Model]], optional):
            Function to retrieve the model instance. Should have the signature
            (path_parameters: Optional[Schema]) -> Model.
        pre_delete (Optional[Callable[[django.http.HttpRequest, Optional[ninja.Schema],
            django.db.models.Model], None]], optional):
            Hook executed before deleting the instance. Should have the signature
            (request: HttpRequest, path_parameters: Optional[Schema], instance: Model)
            -> None.
        post_delete (Optional[Callable[[django.http.HttpRequest, Optional[ninja.Schema],
            django.db.models.Model], None]], optional):
            Hook executed after deleting the instance. Should have the signature
            (request: HttpRequest, path_parameters: Optional[Schema], instance: Model)
            -> None.
        decorators (Optional[List[Callable]], optional): Decorators for the view.
            Defaults to [].
        router_kwargs (Optional[Dict], optional): Additional router arguments, with
            overrides for 'path', 'methods', and 'response' being ignored. Defaults
            to {}.

    Raises:
        django.db.models.ObjectDoesNotExist: If the instance is not found.
        django.db.models.MultipleObjectsReturned: If multiple instances are found.
        django.db.utils.IntegrityError: For database integrity violations on delete.
        ninja.errors.ValidationError: For request components validation issues.

    Important:
        This view does not automatically handle exceptions. It's recommended to
        implement appropriate
        [Exception Handlers](https://django-ninja.dev/guides/errors/) in your project to
        manage such cases effectively, according to your application's needs and
        conventions. See the [Setup](https://django-ninja-crud.readme.io/docs/03-setup)
        guide for more information.

    Example Usage:
    ```python
    delete_department = views.DeleteModelView()

    # or with custom get_model, pre_delete, and post_delete logic
    delete_department = views.DeleteModelView(
        get_model=lambda path_parameters: Department.objects.get(id=path_parameters.id),
        pre_delete=lambda request, path_parameters, instance: None,
        post_delete=lambda request, path_parameters, instance: None,
    )
    ```

    Note:
        The attribute name (e.g., `delete_department`) determines the route's name
        and operation ID in the OpenAPI schema, allowing easy API documentation.
    """

    def __init__(
        self,
        path: str = "/{id}",
        path_parameters: Optional[Schema] = None,
        get_model: Optional[Callable[[Optional[Schema]], Model]] = None,
        pre_delete: Optional[
            Callable[[HttpRequest, Optional[Schema], Model], None]
        ] = None,
        post_delete: Optional[
            Callable[[HttpRequest, Optional[Schema], Model], None]
        ] = None,
        decorators: Optional[List[Callable]] = None,
        router_kwargs: Optional[Dict] = None,
    ) -> None:
        super().__init__(
            method=HTTPMethod.DELETE,
            path=path,
            path_parameters=path_parameters,
            query_parameters=None,
            request_body=None,
            response_body=None,
            response_status=HTTPStatus.NO_CONTENT,
            decorators=decorators,
            router_kwargs=router_kwargs,
        )
        self.get_model = get_model or self.default_get_model
        self.pre_delete = pre_delete or self.default_pre_delete
        self.post_delete = post_delete or self.default_post_delete

    def default_get_model(
        self,
        path_parameters: Optional[Schema],
    ) -> Model:
        """
        Default function to retrieve the model instance to be deleted.

        This method can be overridden with custom logic to retrieve the model instance,
        allowing for advanced retrieval logic, such as adding annotations, filtering
        based on request specifics, or implementing permissions checks, to suit specific
        requirements and potentially improve efficiency and security.

        Args:
            path_parameters (Optional[ninja.Schema]): Deserialized path parameters.

        Returns:
            django.db.models.Model: The model instance to be deleted.

        Raises:
            django.db.models.ObjectDoesNotExist: If no model instance is found.
            django.db.models.MultipleObjectsReturned: If multiple model instances
                are found.
        """
        return self.model_viewset_class.model.objects.get(
            **(path_parameters.dict() if path_parameters else {})
        )

    @staticmethod
    def default_pre_delete(
        request: HttpRequest,
        path_parameters: Optional[Schema],
        instance: Model,
    ) -> None:
        """
        Default pre-delete hook that is called before the model instance is deleted.
        No-op by default.

        This method can be overridden with custom pre-delete logic, such as
        implementing additional checks, permissions, or side effects.

        Args:
            request (django.http.HttpRequest): The request object.
            path_parameters (Optional[ninja.Schema]): Deserialized path parameters.
            instance (django.db.models.Model): The model instance to be deleted.

        Returns:
            None
        """
        pass

    @staticmethod
    def default_post_delete(
        request: HttpRequest,
        path_parameters: Optional[Schema],
        instance: Model,
    ) -> None:
        """
        Default post-delete hook that is called after the model instance is deleted.
        No-op by default.

        This method can be overridden with custom post-delete logic, such as
        implementing additional side effects, logging, or sending notifications.

        Args:
            request (django.http.HttpRequest): The request object.
            path_parameters (Optional[ninja.Schema]): Deserialized path parameters.
            instance (django.db.models.Model): The deleted model instance.

        Returns:
            None
        """
        pass

    def handle_request(
        self,
        request: HttpRequest,
        path_parameters: Optional[Schema],
        query_parameters: Optional[Schema],
        request_body: Optional[Schema],
    ) -> None:
        instance = self.get_model(path_parameters)

        self.pre_delete(request, path_parameters, instance)

        instance.delete()

        self.post_delete(request, path_parameters, instance)
