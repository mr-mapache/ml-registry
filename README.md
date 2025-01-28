# MLRegistry

A simple package to track python objects based on the arguments they were created with. The documentation can be found here: [https://mr-mapache.github.io/ml-registry/](https://mr-mapache.github.io/ml-registry/).

## Table of contents:
- [Introduction](#introduction)
- [Features](#features)
- [Instalation](#instalation)
- [Example](#example)
- [License](#license)

## Introduction

In certain scenarios, such as in machine learning, it's important to keep track of the objects created in your code and associate them with specific entities. For instance, a neural network is not only defined by its name but also by its hyperparameters. This package provides a streamlined way to register objects and retrieve them based on the arguments used during their creation, ensuring efficient tracking and management of these entities.

## Installation

Install the package with pip:

```bash
pip install mlregistry
```

## Example

Suppose you want to create a machine learning model and efficiently track its hyperparameters. Here's an example with a `Perceptron` class:

```python
class Perceptron:
    def __init__(self, input_size: int, output_size: int):
        ...

```

Using the `register` function from the mlregistry package, you can easily achieve this:

```python
from mlregistry import register

register(Perceptron)
```

Once registered, any new object initialized from the Perceptron class will automatically have its creation arguments stored. This makes it simple to track the hyperparameters and assign a unique identity to the object, based on its name and hyperparameters.

```python
from mlregistry import getarguments
from mlregistry import gethash

model = Perceptron(input_size=10, output_size=1)
arguments = getarguments(model) 
hash = gethash(model)  # The hash acts as a locally unique identifier for the object

print(arguments) # {'input_size': 10, 'output_size': 1}
print(hash) # a8657a4057c4f7b3237aec904970630d
```

Notably, an object with the same name and identical arguments will always generate the same hash. This hash acts as a consistent local identifier, effectively treating machine learning models as entities with unique identities defined by their name and hyperparameters.

You can also register objects in a Registry instance. A Registry serves as a collection of types, allowing you to register and retrieve objects by their name.

Here’s an example:

```python

from mlregistry import Registry


class Optimizer:
    def __init__(self, model_params, learning_rate: float):
        ...

registry = Registry[Optimizer]() # Use generics to have PEP484 type hints.
registry.register(Optimizer, excluded_args=[0], excluded_kwargs=['model_params']) 

```

In this example, the `excluded_args` and `excluded_kwargs` parameters are used to omit specific arguments from the hash calculation and the tracked parameters. These options are also available in the standalone `register` function.

Once registered, you can retrieve an object from the registry using its name:

```python

optimizer = registry.get('Optimizer')(model_params={'param':'someparams'}, learning_rate=0.01)
optimizer_arguments = getarguments(optimizer)
print(optimizer_arguments) # {'learning_rate': 0.01} # model_params is excluded from the arguments
```

This feature is especially useful when you need to dynamically list available machine learning models, such as in a REST API, and create a model using only its name and hyperparameters:

```python
print(registry.keys()) # ['Optimizer'] 
print(registry.signature('Optimizer')) # {'learning_rate': float}
```

The package includes additional functionality, which you can explore further in the documentation.

## License

This project is licensed under the MIT License - Use it as you wish in your projects.