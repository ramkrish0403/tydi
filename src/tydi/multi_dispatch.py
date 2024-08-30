from inspect import signature
from typing import Any, Callable, Dict, List, Tuple, get_type_hints, TypeVar
import asyncio
from asyncio import iscoroutinefunction

from beartype.door import is_bearable

T = TypeVar("T")


class MultiMethod:
    def __init__(self, name: str):
        self.name = name
        self.methods: List[Callable] = []

    def register(self, func: Callable):
        self.methods.append(func)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        for method in self.methods:
            if self._match_args(method, args, kwargs):
                if iscoroutinefunction(method):
                    return asyncio.create_task(method(*args, **kwargs))
                return method(*args, **kwargs)
        raise TypeError(
            f"No matching method found for {self.name} with given arguments"
        )

    def _match_args(
        self, func: Callable, args: Tuple[Any, ...], kwargs: Dict[str, Any]
    ) -> bool:
        sig = signature(func)
        try:
            bound_args = sig.bind(*args, **kwargs)
            type_hints = get_type_hints(func)

            for param_name, arg in bound_args.arguments.items():
                if param_name in type_hints:
                    if not is_bearable(arg, type_hints[param_name]):
                        return False
            return True
        except TypeError:
            return False


class MultiDispatch:
    def __init__(self):
        self.registry: Dict[str, MultiMethod] = dict()

    def register(self, func: Callable[..., T]) -> None:
        name = func.__name__
        if name not in self.registry:
            self.registry[name] = MultiMethod(name)
        self.registry[name].register(func)
        return

    def dispatch(self, func: Callable[..., T], *args, **kwargs) -> T:
        name = func.__name__
        if name not in self.registry:
            raise TypeError(
                f"No matching method found for {name} with given arguments"
            )

        multi_method = self.registry[name]
        return multi_method(*args, **kwargs)
