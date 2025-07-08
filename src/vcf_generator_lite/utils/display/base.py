from abc import ABC, abstractmethod
from tkinter import Misc


class Display(ABC):

    @staticmethod
    @abstractmethod
    def get_default_scale_factor(misc: Misc) -> float: ...

    @staticmethod
    @abstractmethod
    def enable_dpi_aware(): ...
