from abc import ABC
from tkinter import Tk, Toplevel
from tkinter.ttk import Style
from typing import override

from vcf_generator_lite.util.tkinter.theme import EnhancedTheme


class BaseTheme(EnhancedTheme, ABC):

    @override
    def apply_tk(self, master: Tk, style: Style):
        # 防止编辑框将其他组件挤出窗口
        master.option_add("*TextFrame.Text.width", 0, "widgetDefault")
        master.option_add("*TextFrame.Text.height", 0, "widgetDefault")

    @override
    def apply_window(self, master: Tk | Toplevel, style: Style): pass
