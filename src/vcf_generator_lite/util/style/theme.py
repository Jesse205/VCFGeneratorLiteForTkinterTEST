from abc import ABC, abstractmethod
from tkinter import Toplevel, Tk


class Theme(ABC):
    @abstractmethod
    def apply_theme(self, master: Tk | Toplevel): pass
