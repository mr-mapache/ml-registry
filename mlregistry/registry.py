from uuid import uuid3, UUID, NAMESPACE_DNS
from datetime import datetime
from inspect import getfullargspec
from typing import Any
from json import dumps
from logging import getLogger
from hashlib import md5
from mlregistry.metadata import Metadata

logger = getLogger(__name__)

def type_signature(type: type, excluded_parameters: set[str]) -> dict[str, str]:
    init = type.__init__
    argspec = getfullargspec(init)
    annotations = { key: (value.__name__ if value is not None else Any.__name__)  for key, value in argspec.annotations.items() }    
    parameters = { key: annotations.get(key, Any.__name__)  for key in argspec.args if key not in excluded_parameters }    
    return parameters

def object_hashing(object: object, args, kwargs, excluded_parameters: set[str]) -> UUID:
    name = object.__class__.__name__
    name += dumps(type_signature(object, excluded_parameters), sort_keys=True)
    for arg in args:
        name += str(arg)
    name += dumps(kwargs, sort_keys=True)
    return md5(name.encode()).hexdigest()

def date_hash(datetime: datetime):
    return md5(datetime.isoformat().encode()).hexdigest()

class Registry[T]:
    def __init__(self, aditional_parameters: dict[str, Any] = None, exclude_parameters: set[str] = None, excluded_positions: list[int] = None):
        self.types = dict()
        self.states = dict()
        self.excluded_postitions = excluded_positions or []
        self.aditional_parameters = aditional_parameters or dict()
        self.excluded_parameters = ( exclude_parameters or set[str]() ) | {'self', 'return'}

    def register(self, type: type):
        signature = type_signature(type, self.excluded_parameters)
        self.types[type.__name__] = (type, signature)
        init = type.__init__

        def wrapper(obj, *args, **kwargs):
            included_args = tuple([ arg for index, arg in enumerate(args) if index not in self.excluded_postitions ])
            included_kwargs = { key: value for key, value in kwargs.items() if key not in self.excluded_parameters } | self.aditional_parameters
            init(obj, *args, **kwargs)
            setattr(obj, '__model__metadata__',
                Metadata(
                    hash=object_hashing(obj, included_args, included_kwargs, self.excluded_parameters),
                    name=type.__name__,
                    args=included_args,
                    kwargs=included_kwargs
                )
            )

            setattr(obj, '__model__signature__', signature)

        type.__init__ = wrapper
        return type    

    def get(self, name: str) -> type[T]:
        type, _ = self.types.get(name)
        return type

    def keys(self) -> list[str]:
        return list(self.types.keys())

    def signature(self, name: str) -> dict[str, str]:
        _, signature = self.types.get(name)
        return signature
    
def get_metadata(object: object) -> Metadata:
    return getattr(object, '__model__metadata__')

def get_signature(object: object) -> dict[str, str]:
    return getattr(object, '__model__signature__')

def get_hash(object: object) -> str:
    return get_metadata(object).hash