from abc import ABC, abstractmethod
from tkinter import Misc
from tkinter.ttk import Style


class Theme(ABC):
    @abstractmethod
    def apply_theme(self, master: Misc, style: Style): pass
