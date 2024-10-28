# ml-registry

Register, manage and track machine learning components easilly, such as PyTorch models and optimizers. You can retrieve component metadata, inspect signatures, and ensure instance integrity through determinant hashes.

## Example

```python
from models import Perceptron
from mlregistry import Registry

# Register components
Registry.register(Perceptron)

```

Now the `Registry` class injected a metadata factory in the `Perceptron` model, metadata that will be created when the model is instantiated. The metadata contains:


- The name of the model, that can be used to retrieve the model instance from the registry and recognize the model during serialization.
- A unique hash of the model instance, usefull for locally identifying the model instance, based on the model's name, signature, and the parameters passed to the constructor.
- A tuple with the model's positional arguments and keyword arguments, that can be used to reconstruct the model instance.
- The model's signature with the model's annotations, usefull for exposing the model's and training using request-response APIs.

```python
from mlregistry import get_metadata, get_hash, get_signature

perceptron = Perceptron(784, 256, 10, p=0.5, bias=True)

### Get metadata, hash, and signature of the model instance
hash = get_hash(perceptron)
print(hash) # 1a79a4d60de6718e8e5b326e338ae533

metadata = get_metadata(perceptron)
print(metadata.name) # Perceptron
print(metadata.args) # (784, 256, 10)
print(metadata.kwargs) # {'p': 0.5, 'bias': True}

signature = get_signature(perceptron)
print(signature) # {input_size: int, hidden_size: int, output_size: int, p: float, bias: bool}

```

Now you can use the `Registry` class to retrieve the model type from the registry.

```python

model_type = Registry.get('Perceptron')
model_instance = model_type(input_size=784, hidden_size=256, output_size=10, p=0.5, bias=True)

assert isinstance(model_instance, Perceptron)

```

It works well with other components as well like optimizers or datasets. For more complex usage it's recommended to create a repository class that will manage the components and their dependencies. This will make it easier to persist the components of your machine learning pipeline.

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

dataset_metada = get_metadata(dataset) # You are now able to serialize the dataset metadata! 

```

Now you will be able to track the components of your machine learning pipeline and serialize them without worrying about given them ugly names that can collide, like "perceptron_model_324" or having to manually track their parameters, since the metadata factory will take care of that for you.