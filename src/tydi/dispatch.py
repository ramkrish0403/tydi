from .multi_dispatch import MultiDispatch
from functools import wraps


def dispatch(dispatcher: MultiDispatch):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return dispatcher.dispatch(func, *args, **kwargs)
        return wrapper
    return decorator
