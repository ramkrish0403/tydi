from functools import wraps

from .multi_dispatch import dispatcher


def dispatch(func):
    dispatcher.register(func)

    @wraps(func)
    def wrapper(*args, **kwargs):
        return dispatcher.dispatch(func, *args, **kwargs)

    return wrapper
