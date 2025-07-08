from abc import ABC
from tkinter import Tk, Toplevel
from tkinter.ttk import Style
from typing import override

from vcf_generator_lite.utils.tkinter.theme import EnhancedTheme


class BaseTheme(EnhancedTheme, ABC):

    @override
    def apply_tk(self, master: Tk, style: Style):
        # 防止编辑框将其他组件挤出窗口
        master.option_add("*ThemedTextFrame.Text.width", 0, "startupFile")
        master.option_add("*ThemedTextFrame.Text.height", 0, "startupFile")

    @override
    def apply_window(self, master: Tk | Toplevel, style: Style):
        pass
