from abc import ABC, abstractmethod
from tkinter import Tk, Toplevel
from tkinter.ttk import Style


class EnhancedTheme(ABC):
    @abstractmethod
    def apply_tk(self, master: Tk, style: Style): pass

    @abstractmethod
    def apply_window(self, master: Tk | Toplevel, style: Style): pass
