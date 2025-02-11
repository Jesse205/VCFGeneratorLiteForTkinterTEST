from tkinter import Toplevel, Tk
from tkinter.ttk import Style

from vcf_generator_lite.theme.base import BaseTheme


class ClamTheme(BaseTheme):
    def apply_theme_with_style(self, master: Tk | Toplevel, style: Style):
        super().apply_theme_with_style(master, style)
        style.theme_use("clam")
        style.configure("TButton", padding="3p")
        style.configure("Vertical.TScrollbar", arrowsize="12p")
        style.configure("TextFrame.TEntry", padding=0, borderwidth="2p")

        window_background = style.lookup("TFrame", "background")
        master.configure(background=window_background)
        master.option_add("*Toplevel.background", window_background)
        master.option_add("*Text.insertWidth", style.lookup("TEntry", "insertwidth"))
        master.option_add("*Text.selectBackground", style.lookup("TEntry", "selectbackground", ["focus"]))
        master.option_add("*Text.selectForeground", style.lookup("TEntry", "selectforeground", ["focus"]))
        master.option_add("*Text.inactiveSelectBackground", style.lookup("TEntry", "selectbackground"))
