from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token

from .models import Profile


def is_manager_user(user):
    if not user or not user.is_authenticated:
        return False
    if user.is_staff:
        return True

    profile = getattr(user, 'profile', None)
    return bool(profile and profile.role == Profile.ROLE_MANAGER)


def manager_token_ttl_seconds(user):
    if not is_manager_user(user):
        return None

    ttl = getattr(settings, 'MANAGER_TOKEN_TTL_SECONDS', 8 * 60 * 60)
    return ttl if ttl and ttl > 0 else None


def issue_auth_token(user):
    if is_manager_user(user) and getattr(settings, 'MANAGER_TOKEN_ROTATE_ON_LOGIN', True):
        Token.objects.filter(user=user).delete()
        return Token.objects.create(user=user)

    token, _ = Token.objects.get_or_create(user=user)
    return token


class BearerOrTokenAuthentication(TokenAuthentication):
    keyword = 'Bearer'

    def authenticate(self, request):
        bearer_result = super().authenticate(request)
        if bearer_result is not None:
            return bearer_result

        self.keyword = 'Token'
        try:
            return super().authenticate(request)
        finally:
            self.keyword = 'Bearer'

    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key)

        ttl = manager_token_ttl_seconds(user)
        if ttl and token.created + timedelta(seconds=ttl) < timezone.now():
            token.delete()
            raise exceptions.AuthenticationFailed('Token has expired.')

        return user, token
