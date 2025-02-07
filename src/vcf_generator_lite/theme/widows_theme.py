from tkinter import Toplevel, Tk
from tkinter.ttk import Style

from vcf_generator_lite.theme.base import BaseTheme


class WindowsTheme(BaseTheme):
    def apply_theme_with_style(self, master: Tk | Toplevel, style: Style):
        super().apply_theme_with_style(master, style)
        style.theme_use("vista")
        style.configure("TButton", padding="2p")
        style.configure("InfoHeader.TFrame", background="systemWindow")

        master.option_add("*Text.selectBackground", style.lookup(".", "selectbackground"))
        master.option_add("*Text.selectForeground", style.lookup(".", "selectforeground"))
        master.option_add("*TextFrame.borderWidth", 2)
