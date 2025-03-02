from tkinter import Misc
from tkinter.font import nametofont
from tkinter.ttk import Style
from typing import override

from vcf_generator_lite.theme.base import BaseTheme


class WindowsTheme(BaseTheme):
    @override
    def apply_theme(self, master: Misc, style: Style):
        super().apply_theme(master, style)
        style.theme_use("vista")
        style.configure("TButton", padding="2.5p")
        style.configure("TextFrame.TEntry", padding=0, borderwidth="1.5p", bordercolor="SystemHighlight")
        style.configure("InfoHeader.TFrame", background="systemWindow")
        style.configure("InfoHeaderContent.TFrame", background="systemWindow")
        style.configure("InfoHeaderContent.TLabel", background="systemWindow")

        menu_font = nametofont("TkMenuFont")
        master.option_add("*Menu.font", menu_font)
