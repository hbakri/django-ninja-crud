from django.contrib.auth.models import User
from django.http import HttpRequest
from ninja.security import HttpBearer


class TokenBearer(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str) -> bool:
        user_queryset = User.objects.filter(id=token)
        if user_queryset.exists():
            return user_queryset.get()
