from tkinter import Toplevel, Tk
from tkinter.ttk import Style
from typing import override

from vcf_generator_lite.theme.base import BaseTheme


class ClamTheme(BaseTheme):
    @override
    def apply_theme_with_style(self, master: Tk | Toplevel, style: Style):
        super().apply_theme_with_style(master, style)
        style.theme_use("clam")
        style.configure("TButton", padding="3p")
        style.configure("Vertical.TScrollbar", arrowsize="12p")
        style.configure("TextFrame.TEntry", padding=0, borderwidth="2p")

        window_background = style.lookup("TFrame", "background")
        master.configure(background=window_background)
        master.option_add("*Toplevel.background", window_background)
