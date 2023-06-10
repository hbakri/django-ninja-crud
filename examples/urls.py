from django.urls import path

from examples.api import api

urlpatterns = [
    path("api/", api.urls),
]
