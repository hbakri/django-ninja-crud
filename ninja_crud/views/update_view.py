from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Type

from django.db.models import ManyToManyField, Model
from django.http import HttpRequest
from pydantic import BaseModel

from ninja_crud.views.api_view import APIView, ViewDecorator, ViewFunction

if TYPE_CHECKING:  # pragma: no cover
    from ninja_crud.viewsets import APIViewSet


class UpdateView(APIView):
    """
    Declarative class-based view for updating a model instance in Django Ninja.

    This class provides a standard implementation for an update view, which retrieves
    a single model instance based on the path parameters, updates the instance based on
    the request body, and saves the changes to the database. It is intended to be used
    in viewsets or as standalone views to simplify the creation of update endpoints.

    Args:
        method (str, optional): The HTTP method for the view. Defaults to "PUT".
        path (str, optional): The URL path for the view. Defaults to "/{id}".
        response_status (int, optional): The HTTP status code for the response.
            Defaults to 200 (OK).
        response_body (Optional[Type[Any]], optional): The response body type.
            Defaults to None. If not provided, the default response body of the viewset
            will be used.
        view_function (Optional[ViewFunction], optional): The function that handles the
            view logic. Default implementation is `default_view_function`, which calls
            `get_model` to retrieve the model instance based on the request and path
            parameters, updates the instance based on the request body, and saves the
            changes to the database.
        view_function_name (Optional[str], optional): The name of the view function.
            Defaults to None, which will use the default function name. If bound to a
            viewset, the function name will be the class attribute name. Useful for
            standalone views outside viewsets.
        path_parameters (Optional[Type[BaseModel]], optional): The path parameters type.
            Defaults to None. If not provided, the default path parameters will be
            resolved based on the model, specified in the viewset or standalone view.
        request_body (Optional[Type[BaseModel]], optional): The request body type.
            Defaults to None. If not provided, the default request body of the viewset
            will be used.
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
        pre_save (Optional[Callable], optional): A callable to perform pre-save
            operations on the model instance. By default, it calls `full_clean` on the
            instance. Useful for custom validation or data processing.
            Should have the signature:
            - `pre_save(request: HttpRequest, instance: Model) -> None`.
        post_save (Optional[Callable], optional): A callable to perform post-save
            operations on the model instance. By default, it does nothing. Useful for
            additional processing or side effects after saving.
            Should have the signature:
            - `post_save(request: HttpRequest, instance: Model) -> None`.

    Example:
    ```python
    from ninja import NinjaAPI
    from ninja_crud import views, viewsets

    from examples.models import Department
    from examples.schemas import DepartmentIn, DepartmentOut

    api = NinjaAPI()

    # Usage as a class attribute in a viewset:
    class DepartmentViewSet(viewsets.APIViewSet):
        api = api
        model = Department
        default_response_body = DepartmentOut
        default_request_body = DepartmentOut

        # Usage with default request and response bodies:
        update_department = views.UpdateView()

        # Usage with explicit request and response bodies:
        update_department = views.UpdateView(
            request_body=DepartmentIn,
            response_body=DepartmentOut,
        )

    # Usage as a standalone view:
    views.UpdateView(
        model=Department,
        request_body=DepartmentIn,
        response_body=DepartmentOut,
        view_function_name="update_department",
    ).add_view_to(api)
    ```
    """

    def __init__(
        self,
        method: str = "PUT",
        path: str = "/{id}",
        response_status: int = 200,
        response_body: Optional[Type[Any]] = None,
        view_function: Optional[ViewFunction] = None,
        view_function_name: Optional[str] = None,
        path_parameters: Optional[Type[BaseModel]] = None,
        request_body: Optional[Type[BaseModel]] = None,
        model: Optional[Type[Model]] = None,
        decorators: Optional[List[ViewDecorator]] = None,
        operation_kwargs: Optional[Dict[str, Any]] = None,
        get_model: Optional[Callable[[HttpRequest, Optional[BaseModel]], Model]] = None,
        pre_save: Optional[Callable[[HttpRequest, Model], None]] = None,
        post_save: Optional[Callable[[HttpRequest, Model], None]] = None,
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
            request_body=request_body,
            model=model,
            decorators=decorators,
            operation_kwargs=operation_kwargs,
        )
        self.get_model = get_model or self.default_get_model
        self.pre_save = pre_save or self.default_pre_save
        self.post_save = post_save or self.default_post_save

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
    def default_pre_save(request: HttpRequest, instance: Model) -> None:
        """
        Default implementation of the pre-save hook for the view. This method calls
        `full_clean` on the model instance to validate the data before saving.
        """
        instance.full_clean()

    @staticmethod
    def default_post_save(request: HttpRequest, instance: Model) -> None:
        """
        Default implementation of the post-save hook for the view. This method does
        nothing by default and can be overridden in init or subclasses to perform
        additional operations after saving the instance.
        """
        pass

    def default_view_function(
        self,
        request: HttpRequest,
        path_parameters: Optional[BaseModel],
        query_parameters: Optional[BaseModel],
        request_body: Optional[BaseModel],
    ) -> Model:
        """
        Default implementation of the view function for the view. This method retrieves
        the model instance based on the path parameters, updates the instance based on
        the request body, calls the pre-save hook to validate the instance, saves the
        changes to the database, and calls the post-save hook for additional
        processing.
        """
        instance = self.get_model(request, path_parameters)

        if request_body is not None:
            for field, value in request_body.dict(exclude_unset=True).items():
                if isinstance(instance._meta.get_field(field), ManyToManyField):
                    getattr(instance, field).set(value)
                else:
                    setattr(instance, field, value)

        self.pre_save(request, instance)
        instance.save()
        self.post_save(request, instance)
        return instance

    def set_api_viewset_class(self, api_viewset_class: Type["APIViewSet"]) -> None:
        """
        Bind the view to a viewset class.

        This method sets the model and path parameters type based on the viewset class,
        and assigns the request body and response body from the viewset class's
        `default_request_body` and `default_response_body`, respectively, if they are
        not already set.

        Note:
            This method is called internally and automatically by the viewset when
            defining views as class attributes. It should not be called manually.
        """
        super().set_api_viewset_class(api_viewset_class)

        if self.request_body is None:
            self.request_body = api_viewset_class.default_request_body

        if self.response_body is None:
            self.response_body = api_viewset_class.default_response_body
