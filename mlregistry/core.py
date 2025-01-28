from typing import Any
from copy import deepcopy
from inspect import signature

def cls_signature(cls: type, excluded_args: list[int] = None, excluded_kwargs: set[str] = None):
    excluded_args = excluded_args or []
    excluded_kwargs = excluded_kwargs or set()
    cls_signature = {}
    for index, (key, value) in enumerate(signature(cls).parameters.items()):
        if index not in excluded_args and key not in excluded_kwargs:
            cls_signature[key] = value.annotation.__name__ if value.annotation != value.empty else "Any"
    return deepcopy(cls_signature)

def cls_parse_args(args: tuple[Any], excluded_args: list[int], signature: dict[str, str]) -> dict[str, Any]: 
    kargs = {}
    for index, (arg, key) in enumerate(zip(args, signature.keys())):
        if index not in excluded_args:
            kargs[key] = arg
    return deepcopy(kargs)

def cls_parse_kwargs(kwargs: dict[str, Any], excluded_kwargs: set[str] = None) -> dict[str, Any]:
    excluded_kwargs = excluded_kwargs or set()
    kargs = {}
    for key, value in kwargs.items():
        if key not in excluded_kwargs:
            kargs[key] = value
    return deepcopy(kargs)
    
def cls_override_init(
    cls: type,
    excluded_args: list[int] = None,
    excluded_kwargs: set[str] = None
):
    init = cls.__init__
    signature = cls_signature(cls)
    def init_wrapper(obj, *args, **kwargs):
        init(obj, *args, **kwargs)
        arguments = cls_parse_args(args, excluded_args, signature) | cls_parse_kwargs(kwargs, excluded_kwargs)
        setattr(obj, '__model__arguments__', arguments)
    cls.__init__ = init_wrapper
    return cls    