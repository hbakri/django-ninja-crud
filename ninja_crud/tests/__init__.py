from .request_components import AuthHeaders, PathParameters, Payloads, QueryParameters
from .test_create import CreateModelViewTest
from .test_delete import DeleteModelViewTest
from .test_list import ListModelViewTest
from .test_partial_update import PartialUpdateModelViewTest
from .test_retrieve import RetrieveModelViewTest, TestRetrieveModelView
from .test_update import TestUpdateModelView, UpdateModelViewTest
from .test_viewset import ModelViewSetTest, TestModelViewSet

__all__ = [
    # request components
    "PathParameters",
    "QueryParameters",
    "AuthHeaders",
    "Payloads",
    # test classes
    "TestModelViewSet",
    "TestRetrieveModelView",
    "TestUpdateModelView",
    # deprecated
    "ModelViewSetTest",
    "ListModelViewTest",
    "CreateModelViewTest",
    "RetrieveModelViewTest",
    "UpdateModelViewTest",
    "PartialUpdateModelViewTest",
    "DeleteModelViewTest",
]
