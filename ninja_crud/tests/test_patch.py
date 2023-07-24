from django.http import HttpResponse

from ninja_crud.tests.test_update import UpdateModelViewTest
from ninja_crud.views.patch import PatchModelView


class PatchModelViewTest(UpdateModelViewTest):
    model_view_class = PatchModelView
    model_view: PatchModelView

    def request_update_model(
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
