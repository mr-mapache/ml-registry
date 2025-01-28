from mlregistry import register
from mlregistry import getarguments
from mlregistry import gethash

class Perceptron:
    def __init__(self, input_size: int, output_size: int):
        ...

register(Perceptron)


model = Perceptron(input_size=10, output_size=1)
arguments = getarguments(model) # {'input_size': 10, 'output_size': 1}
hash = gethash(model) 
print(arguments) # {'input_size': 10, 'output_size': 1}
print(hash) # a8657a4057c4f7b3237aec904970630d




from mlregistry import Registry


class Optimizer:
    def __init__(self, model_params, learning_rate: float):
        ...

registry = Registry()
registry.register(Optimizer, excluded_args=[0], excluded_kwargs=['model_params']) 

optimizer = registry.get('Optimizer')(model_params={'param':'someparams'}, learning_rate=0.01)
optimizer_arguments = getarguments(optimizer)
print(optimizer_arguments) # {'learning_rate': 0.01} # model_params is excluded from the arguments
print(registry.keys()) # ['Optimizer'] 
print(registry.signature('Optimizer')) # {'learning_rate': float}