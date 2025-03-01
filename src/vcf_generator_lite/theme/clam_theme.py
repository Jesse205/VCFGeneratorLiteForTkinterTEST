from tkinter import Tk, Misc
from tkinter.ttk import Style
from typing import override

from vcf_generator_lite.theme.base import BaseTheme


class ClamTheme(BaseTheme):
    @override
    def apply_theme(self, master: Misc, style: Style):
        super().apply_theme(master, style)
        style.theme_use("clam")
        style.configure("TButton", padding="1p")
        style.configure("Vertical.TScrollbar", arrowsize="9p")
        style.configure("InfoHeader.TFrame", relief="raised")
        style.configure("TextFrame.TEntry", padding=0, borderwidth="2p")

        window_background = style.lookup("TFrame", "background")
        if isinstance(master, Tk):
            master.configure(background=window_background)
        master.option_add("*Toplevel.background", window_background)
