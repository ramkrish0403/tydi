import asyncio
import logging
from asyncio import iscoroutinefunction
from inspect import signature
from typing import Any, Callable, Dict, List, Tuple, TypeVar, get_type_hints

from beartype.door import is_bearable

from .inspectors import ClassInspector, MethodInspector, ModuleInspector

logger = logging.getLogger("tydi.multi_dispatch")

T = TypeVar("T")


class MultiMethod:
    def __init__(self, func: Callable, is_inspected: bool = False):
        self.is_inspected = is_inspected
        self.func = func
        self.methods: List[Callable] = []

    def register(self, func: Callable):
        self.methods.append(func)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        for method in self.methods:
            if self._match_args(method, args, kwargs):
                logger.debug(
                    f"Matched the args {args} and kwargs {kwargs} with method signature: {get_type_hints(method)}"
                )
                if iscoroutinefunction(method):
                    return asyncio.create_task(method(*args, **kwargs))
                return method(*args, **kwargs)
        raise TypeError(
            f"No matching method found for {self.func} with given arguments"
        )

    def _match_args(
        self, func: Callable, args: Tuple[Any, ...], kwargs: Dict[str, Any]
    ) -> bool:
        sig = signature(func)
        try:
            bound_args = sig.bind(*args, **kwargs)
            type_hints = get_type_hints(func)
            logger.debug(
                f"\n\nMatching the bound arguments {bound_args.arguments} with func type hints: {type_hints}"
            )
            matched_params = set()
            for param_name, arg in bound_args.arguments.items():
                logger.debug(
                    f"Checking argument: {param_name} = {arg} of type {type(arg)}"
                )
                if param_name in type_hints:
                    if not is_bearable(arg, type_hints[param_name]):
                        logger.debug(
                            f"Argument {param_name} of type {type(arg)} does not match func type hint {type_hints[param_name]}"
                        )
                        return False
                    else:
                        logger.debug(
                            f"Argument {param_name} of type {type(arg)} matches func type hint {type_hints[param_name]}"
                        )
                        matched_params.add(param_name)
                else:
                    return False

            unmatched_params = set()
            for param in sig.parameters:
                if param not in matched_params:
                    unmatched_params.add(param)
            if unmatched_params:
                logger.debug(
                    f"Unmatched parameters: {unmatched_params}, expected parameters: {sig.parameters.keys()}"
                )
                return False
            return True
        except TypeError:
            return False


class MultiDispatch:
    def __init__(self):
        self.registry: Dict[Callable[..., T], MultiMethod] = dict()

    def _is_registered(self, func: Callable[..., T]) -> bool:
        return func in self.registry

    def _get_overloaded_functions(
        self, func: Callable[..., T]
    ) -> List[Callable[..., T]]:
        overloaded_funcs = []
        if MethodInspector.is_class_method(func):
            overloaded_funcs = ClassInspector.get_overloaded_methods(
                MethodInspector.get_name(func),
                MethodInspector.get_class(func),
            )
        elif ModuleInspector.is_module_function(func):
            overloaded_funcs = ModuleInspector.get_overloaded_functions(
                func.__module__, func.__name__
            )
        return overloaded_funcs

    def _register_overloaded_functions(self, func, overloaded_funcs) -> None:
        for _func in overloaded_funcs:
            self.registry[func].register(_func)
        return

    def register(self, func: Callable[..., T]) -> None:
        if self._is_registered(func):
            return

        self.registry[func] = MultiMethod(func, is_inspected=False)
        return

    def dispatch(self, func: Callable[..., T], *args, **kwargs) -> T:
        multi_method = self.registry[func]
        if not multi_method.is_inspected:
            overloaded_funcs = self._get_overloaded_functions(func)
            self._register_overloaded_functions(func, overloaded_funcs)
            self.registry[func].is_inspected = True
        return multi_method(*args, **kwargs)


dispatcher = MultiDispatch()

__all__ = ["dispatcher"]
