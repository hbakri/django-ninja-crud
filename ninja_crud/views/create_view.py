from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Type

from django.db.models import ManyToManyField, Model
from django.http import HttpRequest
from pydantic import BaseModel

from ninja_crud.views.api_view import APIView, ViewDecorator, ViewFunction

if TYPE_CHECKING:  # pragma: no cover
    from ninja_crud.viewsets import APIViewSet


class CreateView(APIView):
    """
    Declarative class-based view for creating a model instance in Django Ninja.

    This class provides a standard implementation for a create view, which creates a
    new model instance based on the request body and saves it to the database. It is
    intended to be used in viewsets or as standalone views to simplify the creation of
    create endpoints.

    Args:
        method (str, optional): The HTTP method for the view. Defaults to "POST".
        path (str, optional): The URL path for the view. Defaults to "/{id}".
        response_status (int, optional): The HTTP status code for the response.
            Defaults to 201 (Created).
        response_body (Optional[Type[Any]], optional): The response body type.
            Defaults to None. If not provided, the default response body of the viewset
            will be used.
        view_function (Optional[ViewFunction], optional): The function that handles the
            view logic. Default implementation is `default_view_function`, which calls
            `init_model` to create a new model instance, sets the instance attributes
            based on the request body, calls the pre-save hook, saves the instance, and
            calls the post-save hook.
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
        init_model (Optional[Callable], optional): A callable to initialize the model
            instance. By default, it creates a new instance of the model using the model
            class defined in the view: `Model()`.
            Should have the signature:
            - `init_model(request: HttpRequest, path_parameters: Optional[BaseModel])
            -> Model`.
        pre_save (Optional[Callable], optional): A callable to perform pre-create
            operations on the model instance. By default, it calls `full_clean` on the
            instance to validate the data before creating.
            Should have the signature:
            - `pre_save(request: HttpRequest, instance: Model) -> None`.
        post_save (Optional[Callable], optional): A callable to perform post-create
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
        create_department = views.CreateView()

        # Usage with explicit request and response bodies:
        create_department = views.CreateView(
            request_body=DepartmentIn,
            response_body=DepartmentOut,
        )

    # Usage as a standalone view:
    views.CreateView(
        model=Department,
        request_body=DepartmentIn,
        response_body=DepartmentOut,
        view_function_name="create_department",
    ).add_view_to(api)
    ```
    """

    def __init__(
        self,
        method: str = "POST",
        path: str = "/",
        response_status: int = 201,
        response_body: Optional[Type[Any]] = None,
        view_function: Optional[ViewFunction] = None,
        view_function_name: Optional[str] = None,
        path_parameters: Optional[Type[BaseModel]] = None,
        request_body: Optional[Type[BaseModel]] = None,
        model: Optional[Type[Model]] = None,
        decorators: Optional[List[ViewDecorator]] = None,
        operation_kwargs: Optional[Dict[str, Any]] = None,
        init_model: Optional[
            Callable[[HttpRequest, Optional[BaseModel]], Model]
        ] = None,
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
        self.init_model = init_model or self.default_init_model
        self.pre_save = pre_save or self.default_pre_save
        self.post_save = post_save or self.default_post_save

    def default_init_model(
        self, request: HttpRequest, path_parameters: Optional[BaseModel]
    ) -> Model:
        """
        Default implementation of the model initialization hook for the view. This
        method creates a new instance of the model using the model class defined in the
        view: `Model()`.
        """
        if self.model is None:
            raise ValueError("No model set for the view.")

        return self.model()

    @staticmethod
    def default_pre_save(request: HttpRequest, instance: Model) -> None:
        """
        Default implementation of the pre-save hook for the view. This method calls
        `full_clean` on the model instance to validate the data before creating.
        """
        instance.full_clean()

    @staticmethod
    def default_post_save(request: HttpRequest, instance: Model) -> None:
        """
        Default implementation of the post-save hook for the view. This method does
        nothing by default and can be overridden in init or subclasses to perform
        additional operations after creating the instance.
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
        Default implementation of the view function for the view. This method creates
        a new instance of the model by calling the `init_model` method, sets the
        instance attributes based on the request body, calls the pre-save hook, saves
        the instance, and calls the post-save hook.

        Note:
            If the request body contains many-to-many fields, they are set after saving
            the instance to ensure that the instance exists in the database before setting
            the many-to-many relationships.
        """
        instance = self.init_model(request, path_parameters)

        m2m_fields_to_set = []
        if request_body:
            for field, value in request_body.dict().items():
                if isinstance(instance._meta.get_field(field), ManyToManyField):
                    m2m_fields_to_set.append((field, value))
                else:
                    setattr(instance, field, value)

        self.pre_save(request, instance)
        instance.save()
        self.post_save(request, instance)

        for field, value in m2m_fields_to_set:
            getattr(instance, field).set(value)

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
