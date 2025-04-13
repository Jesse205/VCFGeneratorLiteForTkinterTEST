from abc import ABC, abstractmethod
from tkinter import Misc


class Display(ABC):

    @abstractmethod
    def get_default_scale_factor(self, misc: Misc) -> float:
        ...

    @abstractmethod
    def enable_dpi_aware(self):
        ...
