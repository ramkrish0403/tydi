from functools import wraps

from .multi_dispatch import MultiDispatch


def dispatch(dispatcher: MultiDispatch):
    def decorator(func):
        dispatcher.register(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return dispatcher.dispatch(func, *args, **kwargs)

        return wrapper

    return decorator
