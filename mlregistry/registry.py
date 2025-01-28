from typing import Any, Optional
from typing import overload
from mlregistry import core 

@overload
def register(cls: type, excluded_args: list[int] = None, excluded_kwargs: set[str] = None):
    """
    A function to override the __init__ method of a class in order to capture the arguments passed
    to it when an instance of the given type is initialized. Can be used as a raw decorator. 
 
    Args:
        cls (type): The class to override the __init__ method.
        excluded_args (list[int], optional): The indexes of the arguments to exclude from the capture. Defaults to None.
        excluded_kwargs (set[str], optional): The names of the keyword arguments to exclude from the capture. Defaults to None.
    
    Returns:
        type: The class with the __init__ method overriden.

    Example:

        .. code-block:: python

        @register
        class Bar:
            def __init__(self, x: int, y: float, z: str):
                pass
                
        class Foo:
            def __init__(self, x: int, y: float, z: str):
                pass
                
        register(Foo, excluded_args=[0], excluded_kwargs=['z'])
    """
    ...

@overload
def register(cls: str, excluded_args: list[int] = None, excluded_kwargs: set[str] = None):
    """
    A decorator to override the __init__ method of a class in order to capture the arguments passed 
    to it when an instance of the given type is initialized. Can be used as a decorator with a name
    argument to set the name of the class in the registry.

    Args:
        cls (str): The name of the class in the registry. Will be retrieved when calling the getname function.
        excluded_args (list[int], optional): The indexes of the arguments to exclude from the capture. Defaults to None.
        excluded_kwargs (set[str], optional): The names of the keyword arguments to exclude from the capture. Defaults to None.
    
    Returns:
        type: A decorator to override the __init__ method of a class.

    Example:
        
        .. code-block:: python

        @register('bar')
        class Bar:
            def __init__(self, x: int, y: float, z: str):
                pass

    """
    ...

def register(cls: type | str | None, excluded_args: list[int] = None, excluded_kwargs: set[str] = None):
    """
    A function to override the __init__ method of a class in order to capture the arguments passed 
    to it when an instance of the given type is initialized. Can be used as a raw decorator or as a
    decorator with a name argument to set the name of the class in the registry.

    Args:
        cls (type | str | None): The class to override the __init__ method or the name of the class in the registry.
        excluded_args (list[int], optional): The indexes of the arguments to exclude from the capture. Defaults to None.
        excluded_kwargs (set[str], optional): The names of the keyword arguments to exclude from the capture. Defaults to None.

    Returns:
        type: The class with the __init__ method overriden or a decorator to override the __init__ method of a class.
    """
    if isinstance(cls, type):
        return core.cls_override_init(cls, excluded_args, excluded_kwargs)
    elif isinstance(cls, str) or cls is None:
        def wrapper(type: type):
            return core.cls_override_init(type, excluded_args, excluded_kwargs, cls)
        return wrapper

class Registry[T]:
    """
    A class to register and retrieve types and their signatures. It acts as collection of types and is usefull in cases
    where a python object needs to be created dynamically based on a string name.

    Attributes:
        types (dict): a dictionary of registered types.
        signatures (dict): a dictionary of registered types signatures.

    Methods:
        register: 
            a decorator to register a type.
        get: 
            get a registered type by name.
        keys: 
            get the list of registered type names.
        signature: 
            get the signature of a registered type by.
    
    
    Example:

        .. code-block:: python

        from mlregistry.registry import Registry

        registry = Registry()

        @registry.register
        class Foo:
            def __init__(self, x: int, y: float, z: str):
                self.x = x
                self.y = y
                self.z = z

        instance = registry.get('Foo')(1, 2.0, '3') # instance of Foo
        signature = registry.signature('Foo') # {'x': 'int', 'y': 'float', 'z': 'str'}
        keys = registry.keys() # ['Foo']
    """
    def __init__(self):
        self.types = dict()
        self.signatures = dict()

    @overload
    def register(self, cls: type, excluded_args: list[int] = None, excluded_kwargs: dict[str, Any] = None) -> type[T]:
        """
        Register a class type with the registry and override its __init__ method in order to capture the arguments
        passed to the constructor during the object instantiation. The captured arguments can be retrieved using the
        `getarguments` function. The `excluded_args` and `excluded_kwargs` parameters can be used to exclude the arguments
        from being captured. 

        Args:
            cls (type): the class type to be registered
            excluded_args (list[int], optional): The list of argument indexes to be excluded. Defaults to None.
            excluded_kwargs (dict[str, Any], optional): The dictionary of keyword arguments to be excluded. Defaults to None.

        Returns:
            type[T]: the registered class type.
        """
        ...

    @overload
    def register(self, cls: str, excluded_args: list[int] = None, excluded_kwargs: dict[str, Any] = None) -> type[T]:
        """
        A decorator to register a class type with the registry and override its __init__ method in order to capture the arguments
        passed to the constructor during the object instantiation. The class type is registered with the name provided as the
        argument to the decorator.

        Args:
            cls (str): the name of the class type to be registered
            excluded_args (list[int], optional): The list of argument indexes to be excluded. Defaults to None.
            excluded_kwargs (dict[str, Any], optional): The dictionary of keyword arguments to be excluded. Defaults to None.

        Returns:
            type[T]: The registered class type with the name provided as the argument to the decorator.
        """
        ...

    def register(self, cls: Any, excluded_args: list[int] = None, excluded_kwargs: dict[str, Any] = None) -> type[T]:
        if isinstance(cls, type):
            self.types[cls.__name__] = cls
            self.signatures[cls.__name__] = core.cls_signature(cls, excluded_args, excluded_kwargs)
            core.cls_override_init(cls, excluded_args, excluded_kwargs)
            
        elif isinstance(cls, str):
            def wrapper(type: type):
                self.types[cls] = type
                self.signatures[cls] = core.cls_signature(type, excluded_args, excluded_kwargs)
                core.cls_override_init(type, excluded_args, excluded_kwargs, cls)
            return wrapper
        

    def get(self, name: str) -> Optional[type[T]]:
        """
        Get a registered type by name from the registry.

        Args:
            name (str): the name of the type to be retrieved

        Returns:
            Optional[type[T]]: the registered type if found, otherwise None
        """
        return self.types.get(name, None)

    def keys(self) -> list[str]:
        '''
        Get the list of registered type names.

        Returns:
            list[str]: the list of registered type names
        '''
        return list(self.types.keys())

    def signature(self, name: str) -> Optional[dict[str, str]]:
        '''
        Get the signature of a registered type by name.

        Parameters:
            name (str): the name of the type to be retrieved.

        Returns:
            dict[str, str]: the signature of the registered type.
        '''
        return self.signatures.get(name, None)