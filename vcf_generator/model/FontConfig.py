from typing import Literal


class FontConfig:
    def __init__(self, family: str, size: int, weight: Literal["normal", "bold"]):
        self.family = family
        self.size = size
        self.weight = weight
