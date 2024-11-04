from uuid import uuid3, UUID, NAMESPACE_DNS
from datetime import datetime
from inspect import getfullargspec
from typing import Optional
from typing import Any
from json import dumps
from logging import getLogger
from hashlib import md5
from dataclasses import dataclass

logger = getLogger(__name__)
from copy import deepcopy

def type_signature(type: type, excluded_positions: list[int], excluded_parameters: set[str]) -> dict[str, str]:
    init = type.__init__
    argspec = getfullargspec(init)
    annotations = {key: (value.__name__ if value is not None else Any.__name__) for key, value in argspec.annotations.items()}
    args = [arg for index, arg in enumerate(argspec.args) if index not in excluded_positions]
    signature = {key: annotations.get(key, Any.__name__) for key in args if key not in excluded_parameters}
    return deepcopy(signature)

def object_parameters(args: list[Any], kwargs: dict[str, Any], signature: dict[str, str]):
    args_dict = { key: value for value, key in zip(args, signature.keys()) }
    kwargs_dict = { key: value for key, value in kwargs.items() if key in signature.keys() }
    return deepcopy(args_dict | kwargs_dict)

def object_hashing(object: object, args: list[Any], kwargs: list[str, Any], excluded_positions: list[int], excluded_parameters: set[str]) -> UUID:
    name = object.__class__.__name__
    parameters = object_parameters(args, kwargs, type_signature(object, excluded_positions, excluded_parameters))
    return md5((name + dumps(parameters, sort_keys=True)).encode()).hexdigest()

@dataclass
class Metadata[T]:
    '''
    Metadata class to store the metadata of an object

    Attributes:
        type (str): the type of the object (should be the same as T, but python does not support this yet)
        hash (str): the hash of the object
        name (str): the name of the object
        arguments (dict[str, Any]): the arguments that were passed to the object during initialization
    '''
    type: str
    hash: str
    name: str
    arguments: dict[str, Any]

class Registry[T]:
    def __init__(self, excluded_positions: list[int] = None, exclude_parameters: set[str] = None):
        self.types = dict()
        self.states = dict()
        self.excluded_positions = excluded_positions or []
        self.excluded_parameters = ( exclude_parameters or set() ) | {'self', 'return'}

    def register(self, type: type, category: str = None) -> type:
        '''
        Register a type in the registry

        Parameters:
            type (type): the type to be registered
            category (str): the category of the type, should be the same as T, but python does not support this yet

        Returns:
            type: the registered type with metadata factory injected in the __init__ method.
        '''

        signature = type_signature(type, self.excluded_positions, self.excluded_parameters)
        self.types[type.__name__] = (type, signature)
        init = type.__init__
        def wrapper(obj, *args, **kwargs):
            init(obj, *args, **kwargs)
            setattr(obj, '__model__metadata__',
                Metadata[T](
                    type=category or 'object',
                    hash=object_hashing(obj, args, kwargs, self.excluded_positions, self.excluded_parameters),
                    name=type.__name__,
                    arguments=object_parameters(args, kwargs, signature)
                )
            )

            setattr(obj, '__model__signature__', signature)

        type.__init__ = wrapper
        return type    

    def get(self, name: str) -> Optional[type[T]]:
        '''
        Get a registered type by name

        Parameters:
            name (str): the name of the type to be retrieved

        Returns:
            type: the registered type
        '''
        pair = self.types.get(name)
        return pair[0] if pair is not None else None

    def keys(self) -> list[str]:
        '''
        Get the list of registered type names

        Returns:
            list[str]: the list of registered type names
        '''
        return list(self.types.keys())

    def signature(self, name: str) -> Optional[dict[str, str]]:
        '''
        Get the signature of a registered type by name

        Parameters:
            name (str): the name of the type to be retrieved

        Returns:
            dict[str, str]: the signature of the registered type
        '''

        pair = self.types.get(name)
        return pair[1] if pair is not None else None
    
def get_date_hash(datetime: datetime):
    '''
    Get the hash of a datetime object

    Parameters:
        datetime (datetime): the datetime object to get the hash from

    Returns:
        str: the hash of the datetime object   
    '''
    return md5(datetime.isoformat().encode()).hexdigest()


    
def get_metadata(object: object) -> Metadata:
    '''
    Get the metadata of an object
    
    Parameters:
        object (object): the object to get the metadata from

    Returns:
        Metadata: the metadata of the object
    '''
    return getattr(object, '__model__metadata__')

def get_signature(object: object) -> dict[str, str]:
    '''
    Get the signature of an object

    Parameters:
        object (object): the object to get the signature from

    Returns:
        dict[str, str]: the signature of the object
    '''
    return getattr(object, '__model__signature__')


def get_hash(object: object) -> str:
    '''
    Get the local identifier of an object

    Parameters:
        object (object): the object to get the hash from

    Returns:
        str: the hash of the object
    '''
    return get_metadata(object).hash