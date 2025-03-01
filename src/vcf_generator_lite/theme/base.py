from abc import ABC
from tkinter import Misc
from tkinter.ttk import Style
from typing import override

from vcf_generator_lite.util.tkinter.theme import Theme


class BaseTheme(Theme, ABC):

    @override
    def apply_theme(self, master: Misc, style: Style):
        master.option_add("*TextFrame.Text.width", 0, "widgetDefault")
        master.option_add("*TextFrame.Text.height", 0, "widgetDefault")
