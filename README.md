# ml-registry

Register, manage, and track machine learning components easily, such as PyTorch models and optimizers. You can retrieve component metadata, inspect signatures, and ensure instance integrity through deterministic hashes.

## Introduction

Tracking machine learning components can be challenging, especially when you have to name them, track their parameters, and ensure the instance you're using matches the one you trained. This library addresses these issues by providing a simple way to register, manage, and track machine learning components, such as models, optimizers, and datasets. It uses cryptographic hashes to create unique identifiers for components based on their names, signatures, and parameters.


## Installation

Install the package with pip:

```bash
pip install mlregistry
```

Using conda:

```
conda install pip
pip install mlregistry
```

## Example
Suppose you have a Perceptron model built with PyTorch. To start using the registry, import the Registry class and register the class you want to track:
```python
from models import Perceptron
from mlregistry import Registry

# Register components
Registry.register(Perceptron)

```

The Registry class injects a metadata factory into the Perceptron model. This metadata includes:

- Model name: Used to retrieve the model instance from the registry and recognize it during serialization.
- Unique hash: Useful for identifying the model instance locally, based on the model’s name, signature, and constructor parameters.
- Arguments: A tuple with positional and keyword arguments for reconstructing the model instance.
- Signature: Includes model annotations, which is useful for exposing the model’s configuration and usage in request-response APIs.

```python
from mlregistry import get_metadata, get_hash, get_signature

registry = Registry() #Create a registry instance before or after registry of classes. 
perceptron = Perceptron(784, 256, 10, p=0.5, bias=True)

# Get metadata, hash, and signature of the model instance
hash = get_hash(perceptron)
print(hash)  # e.g., "1a79a4d60de6718e8e5b326e338ae533"

metadata = get_metadata(perceptron)
print(metadata.arguments)  # {'input_size': 784, 'hidden_size': 256, 'output_size': 10, 'p': 0.5, 'bias': True}

signature = get_signature(perceptron)
print(signature)  # {input_size: int, hidden_size: int, output_size: int, p: float, bias: bool}

```

You can retrieve the model type from the registry:

```python

model_type = registry.get('Perceptron')
model_instance = model_type(input_size=784, hidden_size=256, output_size=10, p=0.5, bias=True)

assert isinstance(model_instance, Perceptron)

```

This works with other components as well, like optimizers and datasets. For complex setups, consider creating a repository class to manage components and dependencies, simplifying pipeline persistence.


```python
from torch.nn import Module, CrossEntropyLoss
from torch.optim import Optimizer, Adam
from torchvision.datasets import MNIST

class Repository:
    models = Registry[Module]()
    criterions = Registry[Module]()
    optimizers = Registry[Optimizer](excluded_positions=[0], exclude_parameters={'params'})
    datasets = Registry[Dataset](excluded_positions=[0], exclude_parameters={'root', 'download'})

Repository.models.register(Perceptron)
Repository.optimizers.register(Adam)
Repository.datasets.register(MNIST)

model = Perceptron(784, 256, 10, p=0.5, bias=True)
criterion = CrossEntropyLoss()
optimizer = Adam(model.parameters(), lr=1e-3)
dataset = MNIST('data', train=True, download=True)

dataset_metadata = get_metadata(dataset)
print(dataset_metadata)  # Serialize dataset metadata

optimizer_metadata = get_metadata(optimizer)
print(optimizer_metadata)  # Excluded parameters like 'params' or the first positional argument won’t appear in metadata
```

This approach enables component tracking and serialization without worrying about naming conflicts or manual parameter tracking.
