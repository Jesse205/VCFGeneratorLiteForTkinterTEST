from tkinter import Toplevel, Tk
from tkinter.ttk import Style
from typing import override

from vcf_generator_lite.theme.base import BaseTheme


class WindowsTheme(BaseTheme):
    @override
    def apply_theme_with_style(self, master: Tk | Toplevel, style: Style):
        super().apply_theme_with_style(master, style)
        style.theme_use("vista")
        style.configure("TButton", padding="2p")
        style.configure("InfoHeader.TFrame", background="systemWindow")
        style.configure("TextFrame.TEntry", padding=0, borderwidth="2p", bordercolor="SystemHighlight")
