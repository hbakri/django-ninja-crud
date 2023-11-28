import json
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Type

import django.http
import django.utils.http

from ninja_crud.views import AbstractModelView

if TYPE_CHECKING:  # pragma: no cover
    from ninja_crud.testing.viewsets import ModelViewSetTestCase


class AbstractModelViewTest(ABC):
    """
    Abstract class for testing model views.

    This class provides a common interface for testing various types of model views. It defines
    several methods that must be implemented by subclasses, including `on_successful_request` and
    `on_failed_request`, which handle the response from the server after a request is made.

    Each test method within this class is automatically attached to the test case when instantiated
    as a class attribute on a `ModelViewSetTestCase` subclass. The test method names are dynamically
    generated based on the class attribute name.

    Attributes:
        model_view (AbstractModelView): The model view to be tested.
        model_viewset_test_case (ModelViewSetTestCase): The test case to which this test belongs.

    Note:
        This is an abstract base class and should not be instantiated directly. Instead, use one of its
        subclasses like `ListModelViewTest`, `CreateModelViewTest`, `RetrieveModelViewTest`,
        `UpdateModelViewTest`, or `DeleteModelViewTest`.
    """

    model_view: AbstractModelView
    model_viewset_test_case: "ModelViewSetTestCase"

    def __init__(self, model_view_class: Type[AbstractModelView]) -> None:
        self.model_view_class = model_view_class

    def handle_request(
        self,
        path_parameters: dict,
        query_parameters: dict,
        headers: dict,
        payload: dict,
    ) -> django.http.HttpResponse:
        """
        Handles the execution of an HTTP request.

        This method constructs the HTTP request and sends it to the server, then returns the server's response.

        Args:
            path_parameters (dict): The path parameters for the request.
            query_parameters (dict): The query parameters for the request.
            headers (dict): The headers to include in the request.
            payload (dict): The payload to send with the request.

        Returns:
            django.http.HttpResponse: The response from the request.
        """
        base_path = self.model_viewset_test_case.base_path.strip("/")
        endpoint_path = self.model_view.path.lstrip("/")
        path = f"/{base_path}/{endpoint_path}"
        return self.model_viewset_test_case.client_class().generic(
            method=self.model_view.method.value,
            path=path.format(**path_parameters),
            QUERY_STRING=django.utils.http.urlencode(query_parameters, doseq=True),
            data=json.dumps(payload),
            content_type="application/json",
            **headers,
        )

    @abstractmethod
    def on_successful_request(
        self,
        response: django.http.HttpResponse,
        path_parameters: dict,
        query_parameters: dict,
        headers: dict,
        payload: dict,
    ):  # pragma: no cover
        """
        Callback method to handle the response for a successful request.

        This method should be overridden in subclasses to implement custom logic for
        processing successful responses.

        Args:
            response (django.http.HttpResponse): The response from the server.
            path_parameters (dict): Path parameters used in the request.
            query_parameters (dict): Query parameters used in the request.
            headers (dict): Headers included in the request.
            payload (dict): Payload sent with the request.
        """
        pass

    @abstractmethod
    def on_failed_request(
        self,
        response: django.http.HttpResponse,
        path_parameters: dict,
        query_parameters: dict,
        headers: dict,
        payload: dict,
    ):  # pragma: no cover
        """
        Callback method to handle the response for a failed request.

        This method should be overridden in subclasses to implement custom logic for
        processing failed responses.

        Args:
            response (django.http.HttpResponse): The response from the server.
            path_parameters (dict): Path parameters used in the request.
            query_parameters (dict): Query parameters used in the request.
            headers (dict): Headers included in the request.
            payload (dict): Payload sent with the request.
        """
        pass

    def bind_to_model_viewset_test_case(
        self, model_viewset_test_case: "ModelViewSetTestCase"
    ) -> None:
        self.model_viewset_test_case = model_viewset_test_case

    def bind_to_model_view(self, model_view: AbstractModelView) -> None:
        self.model_view = model_view
