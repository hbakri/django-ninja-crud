from typing import Any, Callable, Dict, List, Optional, Type

from django.db.models import Model
from django.http import HttpRequest
from pydantic import BaseModel

from ninja_crud.views.api_view import APIView, ViewDecorator, ViewFunction


class DeleteView(APIView):
    """
    Declarative class-based view for deleting a model instance in Django Ninja.

    This class provides a standard implementation for a delete view, which retrieves
    a single model instance based on the path parameters and deletes it. It is
    intended to be used in viewsets or as standalone views to simplify the creation
    of delete endpoints.

    Args:
        method (str, optional): The HTTP method for the view. Defaults to "DELETE".
        path (str, optional): The URL path for the view. Defaults to "/{id}".
        response_status (int, optional): The HTTP status code for the response.
            Defaults to 204 (No Content).
        response_body (Optional[Type[Any]], optional): The response body type.
            Defaults to None.
        view_function (Optional[ViewFunction], optional): The function that handles
            the view logic. Default implementation is `default_view_function`, which
            calls `get_model` to retrieve the model instance based on the request
            and path parameters, calls the pre-delete hook, deletes the instance,
            and calls the post-delete hook.
        view_function_name (Optional[str], optional): The name of the view function.
            Defaults to None, which will use the default function name. If bound to
            a viewset, the function name will be the class attribute name. Useful for
            standalone views outside viewsets.
        path_parameters (Optional[Type[BaseModel]], optional): The path parameters type.
            Defaults to None. If not provided, the default path parameters will be
            resolved based on the model, specified in the viewset or standalone view.
        model (Optional[Type[Model]], optional): The Django model associated with the
            view. Defaults to None. Mandatory if not bound to a viewset, otherwise
            inherited from the viewset.
        decorators (Optional[List[ViewDecorator]], optional): List of decorators to
            apply to the view function. Decorators are applied in reverse order.
        operation_kwargs (Optional[Dict[str, Any]], optional): Additional keyword
            arguments for the operation.
        get_model (Optional[Callable], optional): A callable to retrieve the model
            instance. By default, it gets the model instance based on the path
            parameters. Useful for customizing the model retrieval logic, for example,
            for optimizing queries or handling errors. Should have the signature:
            - `get_model(request: HttpRequest, path_parameters: Optional[BaseModel])
            -> Model`.
        pre_delete (Optional[Callable], optional): A callable to perform pre-delete
            operations on the model instance. By default, it does nothing. Useful for
            additional operations before deleting the instance.
            Should have the signature:
            - `pre_delete(request: HttpRequest, instance: Model) -> None`.
        post_delete (Optional[Callable], optional): A callable to perform post-delete
            operations on the model instance. By default, it does nothing. Useful for
            additional operations after deleting the instance.
            Should have the signature:
            - `post_delete(request: HttpRequest, instance: Model) -> None`.

    Example:
    ```python
    from ninja import NinjaAPI
    from ninja_crud import views, viewsets

    from examples.models import Department

    api = NinjaAPI()

    # Usage as a class attribute in a viewset:
    class DepartmentViewSet(viewsets.APIViewSet):
        api = api
        model = Department

        delete_department = views.DeleteView()

    # Usage as a standalone view:
    views.DeleteView(
        model=Department,
        view_function_name="delete_department",
    ).add_view_to(api)
    ```
    """

    def __init__(
        self,
        method: str = "DELETE",
        path: str = "/{id}",
        response_status: int = 204,
        response_body: Optional[Type[Any]] = None,
        view_function: Optional[ViewFunction] = None,
        view_function_name: Optional[str] = None,
        path_parameters: Optional[Type[BaseModel]] = None,
        model: Optional[Type[Model]] = None,
        decorators: Optional[List[ViewDecorator]] = None,
        operation_kwargs: Optional[Dict[str, Any]] = None,
        get_model: Optional[Callable[[HttpRequest, Optional[BaseModel]], Model]] = None,
        pre_delete: Optional[Callable[[HttpRequest, Model], None]] = None,
        post_delete: Optional[Callable[[HttpRequest, Model], None]] = None,
    ) -> None:
        super().__init__(
            method=method,
            path=path,
            response_status=response_status,
            response_body=response_body,
            view_function=view_function or self.default_view_function,
            view_function_name=view_function_name,
            path_parameters=path_parameters,
            query_parameters=None,
            request_body=None,
            model=model,
            decorators=decorators,
            operation_kwargs=operation_kwargs,
        )
        self.get_model = get_model or self.default_get_model
        self.pre_delete = pre_delete or self.default_pre_delete
        self.post_delete = post_delete or self.default_post_delete

    def default_get_model(
        self, request: HttpRequest, path_parameters: Optional[BaseModel]
    ) -> Model:
        """
        Default implementation of the model retrieval logic for the view.

        This method retrieves the model instance based on the path parameters. For
        example, if the path is `/{id}`, it will fetch the model instance with
        the corresponding id value: `Model.objects.get(id=path_parameters.id)`.
        """
        if self.model is None:
            raise ValueError("No model set for the view.")

        return self.model.objects.get(
            **(path_parameters.dict() if path_parameters else {})
        )

    @staticmethod
    def default_pre_delete(request: HttpRequest, instance: Model) -> None:
        """
        Default implementation of the pre-delete logic for the view. This method does
        nothing by default and can be overridden in init or subclasses to perform
        additional operations before deleting the instance.
        """
        pass

    @staticmethod
    def default_post_delete(request: HttpRequest, instance: Model) -> None:
        """
        Default implementation of the post-delete logic for the view. This method does
        nothing by default and can be overridden in init or subclasses to perform
        additional operations after deleting the instance.
        """
        pass

    def default_view_function(
        self,
        request: HttpRequest,
        path_parameters: Optional[BaseModel],
        query_parameters: Optional[BaseModel],
        request_body: Optional[BaseModel],
    ) -> None:
        """
        Default implementation of the view function for the view. This method retrieves
        the model instance based on the path parameters, calls the pre-delete hook,
        deletes the instance, and calls the post-delete hook.

        This method does not return a response body, as the instance is deleted and
        the response status is set to 204 (No Content).
        """
        instance = self.get_model(request, path_parameters)

        self.pre_delete(request, instance)
        instance.delete()
        self.post_delete(request, instance)
