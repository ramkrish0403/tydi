import importlib
import inspect
from typing import Callable, List

from ..overload import get_overloads


class ModuleInspector:

    @staticmethod
    def is_module_function(func: Callable) -> bool:
        return inspect.isfunction(func) and not inspect.ismethod(func)

    @staticmethod
    def get_overloaded_functions(
        module_name: str, function_name: str
    ) -> List[Callable]:
        """
        Retrieve all overloaded functions with the given name from the specified module.

        Args:
            module_name (str): The name of the module to inspect.
            function_name (str): The name of the function to find overloads for.

        Returns:
            List[Callable]: A list of Callable objects representing the overloaded functions.
        """
        try:
            # Ensure the module is imported and get a reference to it
            module = importlib.import_module(module_name)
        except ImportError:
            raise ImportError(f"Module '{module_name}' could not be imported.")

        # Get the function object
        func = getattr(module, function_name, None)
        if func is None:
            return []

        # Get the overloads
        overloads = get_overloads(func)

        # If no overloads are found, it might mean the function isn't overloaded,
        # or we're using a Python version earlier than 3.11
        if not overloads:
            return [func] if hasattr(func, "__overload__") else []

        return list(overloads)
