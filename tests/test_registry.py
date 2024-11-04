from pytest import fixture
from mlregistry.registry import Registry, get_metadata, get_signature, get_hash

class Model:
    def params(self) -> dict: ...

class Perceptron:
    def __init__(self, input_size, hidden_size: int, output_size: int, p: float, activation):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.p = p
        self.activation = activation

    def params(self) -> dict:
        return {
            'weights': [1,2,3]
        }

class Optimizer:
    def __init__(self, params: dict, lr: float):
        self.params = params
        self.lr = lr

class Repository:
    models = Registry[Model]() # optional generic parameter to use pep484 type hints
    optimizers = Registry[Optimizer](excluded_positions=[0], exclude_parameters={'params'})

@fixture
def repository():
    Repository.models.register(Perceptron)
    Repository.optimizers.register(Optimizer)
    return Repository()

def test_metadata(repository: Repository):    
    model = Perceptron(10, 20, 30, p=0.5, activation='relu')
    optimizer = Optimizer(params=model.params(), lr=0.01)

    model_hash = get_hash(model)
    assert len(model_hash) == 32 and all(c in "0123456789abcdefABCDEF" for c in model_hash), "Not a valid MD5 hash format."

    model_metadata = get_metadata(model)
    print(model_metadata.arguments)
    assert model_metadata.arguments == {
        'input_size': 10,
        'hidden_size': 20,
        'output_size': 30,
        'p': 0.5, 
        'activation': 'relu'
    }
    assert model_metadata.name == 'Perceptron'

    optimizer_metadata = get_metadata(optimizer)
    assert optimizer_metadata.arguments == {'lr': 0.01}

    model_signature = get_signature(model)
    assert model_signature == {'input_size': 'Any', 'hidden_size': 'int', 'output_size': 'int', 'p': 'float', 'activation': 'Any'}
    

def test_retrieval(repository: Repository):
    model_type = Repository.models.get('Perceptron')
    model_instance = model_type(10, 20, 30, p=0.5, activation='relu')
    assert model_instance.params() == {'weights': [1,2,3]}

    optimizer_type = Repository.optimizers.get('Optimizer')
    optimizer_instance = optimizer_type(params=model_instance.params(), lr=0.01)
    assert optimizer_instance.params == {'weights': [1,2,3]}
    assert optimizer_instance.lr == 0.01

def test_keys(repository: Repository):
    assert Repository.models.keys() == ['Perceptron']
    assert Repository.optimizers.keys() == ['Optimizer']