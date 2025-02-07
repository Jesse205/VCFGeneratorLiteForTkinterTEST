from tkinter import Toplevel, Tk
from tkinter.font import nametofont
from tkinter.ttk import Style
from typing import final, override

from vcf_generator_lite.util.style.theme import Theme


class BaseTheme(Theme):

    @final
    @override
    def apply_theme(self, master: Tk | Toplevel):
        font = nametofont("TkDefaultFont")
        font.configure(size=12)
        master.option_add("*font", font, "widgetDefault")
        style = Style(master)
        self.apply_theme_with_style(master, style)

    def apply_theme_with_style(self, master: Tk | Toplevel, style: Style): pass
