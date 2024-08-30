from .multi_dispatch import MultiDispatch
from functools import wraps


def register(dispatcher: MultiDispatch):
    def decorator(func):
        dispatcher.register(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return
        return wrapper
    return decorator
