from tkinter import Misc
from tkinter.ttk import Style
from typing import override

from vcf_generator_lite.theme.base import BaseTheme


class WindowsTheme(BaseTheme):
    @override
    def apply_theme(self, master: Misc, style: Style):
        super().apply_theme(master, style)
        style.theme_use("vista")
        style.configure("TButton", padding="1p")
        style.configure("InfoHeader.TFrame", background="systemWindow")
        style.configure("TextFrame.TEntry", padding=0, borderwidth="2p", bordercolor="SystemHighlight")
