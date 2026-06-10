from uuid import uuid4

from .logging_context import set_request_context


class RequestContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.headers.get('X-Request-ID') or uuid4().hex
        request.request_id = request_id
        user = getattr(request, 'user', None)
        user_id = user.id if getattr(user, 'is_authenticated', False) else '-'
        set_request_context(request_id, user_id)

        response = self.get_response(request)
        response['X-Request-ID'] = request_id
        return response
