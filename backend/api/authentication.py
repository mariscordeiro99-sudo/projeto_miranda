from rest_framework.authentication import TokenAuthentication


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
