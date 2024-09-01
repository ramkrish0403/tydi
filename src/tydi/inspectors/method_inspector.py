import inspect
import sys
import types
from typing import Type, Union


class MethodInspector:

    @staticmethod
    def is_class_method(method: object) -> bool:
        """
        Check if the provided object is a class method.

        :param method: The object to check.
        :return: True if the object is a method or a function, otherwise False.
        """
        return (
            inspect.ismethod(method)
            or inspect.isfunction(method)
            and hasattr(method, "__qualname__")
            and "." in method.__qualname__
        )

    @staticmethod
    def get_name(method: Union[types.MethodType, types.FunctionType]) -> str:
        """
        Get the name of the method or function.

        :param method: The method or function to inspect.
        :return: The name of the method or function.
        """
        return method.__name__

    @staticmethod
    def get_class(method: Union[types.MethodType, types.FunctionType]) -> Type:
        """
        Get the class of the method or function.

        :param method: The method or function to inspect.
        :return: The class that defines the method or function.
        """
        print(type(method))
        if isinstance(method, property):
            method = method.fget

        if hasattr(method, "__self__"):
            # Bound method
            return method.__self__.__class__
        
        # Extract the class name from __qualname__
        class_name = method.__qualname__.split(".<locals>", 1)[0].rsplit(".", 1)[0]

        # Get the module where the method is defined
        module_name = method.__module__
        module = sys.modules[module_name]

        # Retrieve and return the class object
        return getattr(module, class_name)

    @staticmethod
    def get_class_name(
        method: Union[types.MethodType, types.FunctionType],
    ) -> str:
        """
        Get the class name of the method or function.

        :param method: The method or function to inspect.
        :return: The name of the class that defines the method or function.
        """
        return method.__qualname__.split(".<locals>", 1)[0].rsplit(".", 1)[0]
