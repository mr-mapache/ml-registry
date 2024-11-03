'''
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

def type_signature(object: object, excluded_parameters: set[str] = set()) -> dict[str, str]:
    init = object.__init__
    argspec = getfullargspec(init)
    annotations = { key: (value.__name__ if value is not None else Any.__name__)  for key, value in argspec.annotations.items() }    
    parameters = { key: annotations.get(key, Any.__name__)  for key in argspec.args if key not in excluded_parameters }    
    return parameters

def object_parameters(args: list[Any], kwargs: list[str, Any], signature: dict[str, str]):
    return { key: value for value, key in zip(args, signature.keys()) } | kwargs

def object_hashing(object: object, args: list[Any], kwargs: list[str, Any], excluded_parameters: set[str]) -> UUID:
    name = object.__class__.__name__
    parameters = object_parameters(args, kwargs, type_signature(object, excluded_parameters))
    print((name + dumps(parameters, sort_keys=True)))
    return md5((name + dumps(parameters, sort_keys=True)).encode()).hexdigest()

class Perceptron:
    def __init__(self, input_size: int, hidden_size: int, output_size: int, p: float):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.p = p

    def params(self):
        return {"1", "2", "3"}
    
class Optimizer:
    def __init__(self, params: set, lr: float):
        self.params = params
        self.lr = lr

model = Perceptron(784, 256, 10, p=0.5)
optimizer = Optimizer(model.params(), lr=0.5)

signature = {"input_size": "int", "hidden_size": "int", "output_size": "int", "p": "float"}
args = [784, 256, 10]
kwargs = {"p": 0.5}

signature = {"lr": "float"}
args = []
kwargs = {"lr": 0.1}
excluded_positions = [0]

print(object_hashing(optimizer, args, kwargs, {'self'}))

'''