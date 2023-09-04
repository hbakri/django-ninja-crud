from .request_components import AuthHeaders, PathParameters, Payloads, QueryParameters
from .test_create import CreateModelViewTest, TestCreateModelView
from .test_delete import DeleteModelViewTest, TestDeleteModelView
from .test_list import ListModelViewTest, TestListModelView
from .test_partial_update import PartialUpdateModelViewTest, TestPartialUpdateModelView
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
    "TestListModelView",
    "TestCreateModelView",
    "TestRetrieveModelView",
    "TestUpdateModelView",
    "TestPartialUpdateModelView",
    "TestDeleteModelView",
    # deprecated
    "ModelViewSetTest",
    "ListModelViewTest",
    "CreateModelViewTest",
    "RetrieveModelViewTest",
    "UpdateModelViewTest",
    "PartialUpdateModelViewTest",
    "DeleteModelViewTest",
]
