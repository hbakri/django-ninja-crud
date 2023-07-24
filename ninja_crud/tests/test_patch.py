from django.http import HttpResponse

from ninja_crud.tests import AuthHeaders, PathParameters, Payloads
from ninja_crud.tests.request_composer import ArgOrCallable, TestCaseType
from ninja_crud.tests.test_update import UpdateModelViewTest
from ninja_crud.views.patch import PatchModelView


class PatchModelViewTest(UpdateModelViewTest):
    model_view_class = PatchModelView
    model_view: PatchModelView

    def __init__(
        self,
        path_parameters: ArgOrCallable[PathParameters, TestCaseType],
        payloads: ArgOrCallable[Payloads, TestCaseType],
        auth_headers: ArgOrCallable[AuthHeaders, TestCaseType] = None,
    ) -> None:
        super().__init__(path_parameters, payloads, auth_headers)
        self.request_composer.request_method = self.request_patch_model

    def request_patch_model(
        self,
        path_parameters: dict,
        query_parameters: dict,
        auth_headers: dict,
        payload: dict,
    ) -> HttpResponse:
        path = "/" + self.model_view_set_test.urls_prefix + self.model_view.get_path()
        return self.model_view_set_test.client_class().patch(
            path=path.format(**path_parameters),
            data=payload,
            content_type="application/json",
            **auth_headers,
        )
