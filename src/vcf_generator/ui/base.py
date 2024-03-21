from tkinter import *
import tkinter.font as tk_font
from vcf_generator.util import display
from vcf_generator.util.display import get_window_dpi_scaling

__all__ = ["BaseWindow"]

default_font_list = [
    ("Microsoft YaHei UI", 9)
]
display.set_process_dpi_aware(display.WinDpiAwareness.PROCESS_SYSTEM_DPI_AWARE)


class BaseWindow(Tk):
    def __init__(self):
        super().__init__()
        self._dpi_scaling = get_window_dpi_scaling(self)
        self.iconbitmap("./assets/icon.ico")
        families = tk_font.families(self)
        for font in default_font_list:
            if font[0] in families:
                self.option_add("*font", font)
                break

    def get_scaled(self, size: int):
        return int(size * self._dpi_scaling)

    def set_size(self, width: int, height: int):
        self.geometry(f"{self.get_scaled(width)}x{self.get_scaled(height)}")

    def set_minsize(self, width: int, height: int):
        self.minsize(self.get_scaled(width), self.get_scaled(height))
