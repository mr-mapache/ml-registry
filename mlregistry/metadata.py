from typing import Any
from dataclasses import dataclass

@dataclass
class Metadata:
    hash: str
    name: str
    args: tuple
    kwargs: dict[str, Any]