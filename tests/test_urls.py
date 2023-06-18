from django.urls import path

from tests.test_api import api

urlpatterns = [
    path("api/", api.urls),
]
