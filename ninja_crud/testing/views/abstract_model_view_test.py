import json
from typing import TYPE_CHECKING, Type

import django.http
from django.utils.http import urlencode

from ninja_crud.views import AbstractModelView

if TYPE_CHECKING:  # pragma: no cover
    from ninja_crud.testing.viewsets import ModelViewSetTestCase


class AbstractModelViewTest:
    """
    Base class for testing model views.

    This class provides common functionalities for testing various CRUD operations
    associated with a Django Ninja model view. It handles the setup and execution
    of HTTP requests for different test scenarios.

    Attributes:
        model_viewset_test_case (ModelViewSetTestCase): The test case class that
            contains the model viewset to be tested.
        model_view_class (Type[AbstractModelView]): The model view class to be tested.
        model_view (AbstractModelView): The model view instance to be tested that is
            retrieved from the model viewset.
    """

    model_viewset_test_case: "ModelViewSetTestCase"
    model_view: AbstractModelView

    def __init__(self, model_view_class: Type[AbstractModelView]) -> None:
        """
        Initialize the model view test.

        Args:
            model_view_class (Type[AbstractModelView]): The class of the model view to be tested.
        """
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
            QUERY_STRING=urlencode(query_parameters, doseq=True),
            data=json.dumps(payload),
            content_type="application/json",
            **headers,
        )

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
