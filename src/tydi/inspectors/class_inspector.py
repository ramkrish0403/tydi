import inspect
from types import FunctionType
from typing import Callable, Dict, List, Type

from ..overload import get_overloads


class ClassInspector:
    """
    A utility class for inspecting class information, including methods,
    superclasses, and method resolution order (MRO).
    """

    @staticmethod
    def get_class_name(cls: Type) -> str:
        """
        Get the name of the class.

        Args:
            cls (Type): The class type to inspect.

        Returns:
            str: The name of the class.
        """
        return cls.__name__

    @staticmethod
    def get_superclasses(cls: Type) -> tuple[type, ...]:
        """
        Get a list of all superclasses of the given class.

        Args:
            cls (Type): The class type to inspect.

        Returns:
            List[Type]: A list of superclasses of the class.
        """
        return cls.__mro__[1:]  # Skip the class itself

    @staticmethod
    def get_all_methods(cls: Type) -> Dict[str, List[FunctionType]]:
        """
        Get all methods of the class, including inherited methods.

        Args:
            cls (Type): The class type to inspect.

        Returns:
            Dict[str, List[FunctionType]]: A dictionary where keys are method names and values are method functions.
        """
        methods: Dict[str, List[FunctionType]] = {}
        for cls in inspect.getmro(cls):
            for name, func in inspect.getmembers(
                cls,
                predicate=inspect.isfunction,
                # predicate=inspect.ismethod,
            ):
                if name not in methods:
                    methods[name] = []
                methods[name].append(func)
        return methods

    @staticmethod
    def get_method_mro(method_name: str, cls: Type) -> List[Callable]:
        """
        Get the method resolution order (MRO) for a given method name.

        Args:
            method_name (str): The name of the method to inspect.
            cls (Type): The class type to inspect.

        Returns:
            List[Callable]: A list of methods of same name in MRO.
        """
        method_mro = []
        for base in inspect.getmro(cls):
            if method_name in base.__dict__:
                method = base.__dict__[method_name]
                method_mro.append(method)
        return method_mro

    @staticmethod
    def get_overloaded_methods(method_name: str, cls: Type) -> List[Callable]:
        """
        Get all overloaded methods with the given name in the current class.

        Args:
            method_name (str): The name of the method to inspect.
            cls (Type): The class type to inspect.

        Returns:
            List[Callable]: A list of overloaded methods with the given name.
        """
        methods = []
        class_dict = vars(cls)
        if method_name in class_dict:
            method = class_dict[method_name]
            if isinstance(method, classmethod):
                method = method.__func__
            overloads = get_overloads(method)
            if overloads:
                methods.extend(overloads)
            else:
                methods.append(method)
        return methods
