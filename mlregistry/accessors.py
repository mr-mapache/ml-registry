from typing import Any
from json import dumps
from hashlib import md5
from copy import deepcopy

def getarguments(obj: object) -> dict[str, Any]:
    """
    A function to get the arguments captured by the __init__ method of a class when an instance of the
    given type is initialized.

    Args:
        obj (object): The object to get the arguments from.

    Raises:
        AttributeError: If the object was not registered.

    Returns:
        dict[str, Any]: The arguments captured by the __init__ method of the object.
    """
    if not hasattr(obj, '__model__arguments__'):
        raise AttributeError(f"The object {obj} was not registered")
    return getattr(obj, '__model__arguments__')

def getname(obj: object) -> str:
    """
    A function to get the name of the object. If the object has a __model__name__ attribute, it will be
    returned. Otherwise, the class name will be returned.

    Args:
        obj (object): The object to get the name from.

    Returns:
        str: The name of the object.
    """
    if hasattr(obj, '__model__name__'):
        return getattr(obj, '__model__name__')
    else:
        return obj.__class__.__name__

def gethash(obj: object) -> str:
    """
    A function to get an unique deterministic hash of the object calculated from the name and the arguments
    captured by the __init__ method of the object. If the object was not registered, an AttributeError will be
    raised. The hash will be calculated using the md5 algorithm by default but can be setted manually using the
    sethash function.

    Args:
        obj (object): The object to get the hash from.

    Returns:
        str: The hash of the object.

    Raises:
        AttributeError: If the object was not registered and does not have a hash setted. 
    """
    if not hasattr(obj, '__model__arguments__') and not hasattr(obj, '__model__hash__'):
        raise AttributeError(f"The object {obj} was not registered and does not have a hash")
    
    if hasattr(obj, '__model__hash__'):
        return getattr(obj, '__model__hash__')
    else:
        arguments = getarguments(obj)
        return md5((getname(obj) + dumps(arguments)).encode()).hexdigest()

def sethash(obj: object, hash: str = None) -> None:
    """
    A function to set the hash of the object. If the hash is not provided, it will be calculated using the
    md5 algorithm from the name and the arguments captured by the __init__ method of the object by default.
    If a hash is provided, it will be setted as the hash of the object.

    Args:
        obj (object): _description_
        hash (str, optional): _description_. Defaults to None.
    """
    if not hash:
        setattr(obj, '__model__hash__', gethash(obj))
    else:
        setattr(obj, '__model__hash__', hash)

def setname(obj: object, name: str = None) -> None:
    """
    A function to set the name of the object. If the name is not provided, it will be retrieved from the
    class name. If a name is provided, it will be setted as the name of the object.

    Args:
        obj (object): The object to set the name.
        name (str, optional): The name to set. Defaults to None.
    """
    if not name:
        setattr(obj, '__model__name__', getname(obj))
    else:
        setattr(obj, '__model__name__', name)


def getmetadata(obj: object) -> dict[str, Any]:
    """
    A function to get the metadata of the object. The metadata is a dictionary containing the name, the
    arguments and the hash of the object.

    Args:
        obj (object): The object to get the metadata.

    Returns:
        dict[str, Any]: The metadata of the object.
    """
    hash_field = {'hash': getattr(obj, '__model__hash__')} if hasattr(obj, '__model__hash__') else {}
    name_field = {'name': getattr(obj, '__model__name__')} if hasattr(obj, '__model__name__') else {}
    arguments_field = {'arguments': getattr(obj, '__model__arguments__')} if hasattr(obj, '__model__arguments__') else {}
    return deepcopy(hash_field | name_field | arguments_field)