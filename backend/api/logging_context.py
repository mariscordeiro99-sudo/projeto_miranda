import logging
from contextvars import ContextVar


request_id_context = ContextVar('request_id', default='-')
user_id_context = ContextVar('user_id', default='-')


class RequestContextFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_context.get()
        record.user_id = user_id_context.get()
        return True


def set_request_context(request_id, user_id='-'):
    request_id_context.set(request_id or '-')
    user_id_context.set(str(user_id or '-'))
