from abc import ABC
from tkinter import Tk
from tkinter.ttk import Style

from vcf_generator_lite.themes.abs import ThemePatch


class BaseThemePatch(ThemePatch, ABC):
    style: Style

    def __init__(self, app: Tk):
        self.style = Style(app)
        background = self.style.lookup("TFrame", "background")
        # 防止编辑框将其他组件挤出窗口
        app.option_add("*ThemedText.Text.width", 0, "startupFile")
        app.option_add("*ThemedText.Text.height", 0, "startupFile")

        # 使用 Sizegrip 调节窗口大小时可能会露出窗口背景，需要单独修改窗口背景色以避免露出破绽。
        app.configure(background=background)
        app.option_add("*Toplevel", background, "startupFile")
