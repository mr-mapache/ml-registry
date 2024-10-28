from typing import Any

class Metadata:
    def __init__(self, hash: str, name: str, args: set, kwargs: dict[str, Any]):
        self.hash = hash
        self.name = name
        self.args = args
        self.kwargs = kwargs