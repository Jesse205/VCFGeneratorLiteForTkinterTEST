from tkinter import Tk
from tkinter.font import nametofont
from typing import override

from vcf_generator_lite.themes.base import BaseThemePatch


class VistaThemePatch(BaseThemePatch):
    @override
    def __init__(self, app: Tk):
        super().__init__(app)

        treeview_font = nametofont(self.style.lookup("Treeview", "font", default="TkDefaultFont"))
        treeview_font_metrics = treeview_font.metrics()

        # 重写部分配置以适配高分屏
        self.style.configure("TButton", padding="2.5p")
        self.style.configure("Treeview", rowheight=treeview_font_metrics.get("linespace") + app.winfo_pixels("2.5p"))
        self.style.configure("Heading", padding="1.5p")

        # 自定义组件
        self.style.configure("ThemedText.TEntry", padding=0, borderwidth="1.5p")
        self.style.configure("DialogHeader.TFrame", background="systemWindow")
        self.style.configure("DialogHeaderContent.TFrame", background="systemWindow")
        self.style.configure("DialogHeaderContent.TLabel", background="systemWindow")

        select_background = self.style.lookup("TEntry", "selectbackground", ["focus"])
        app.option_add("*ThemedText.Text.inactiveSelectBackground", select_background, "startupFile")

        # Windows 7 中菜单默认不使用 TkMenuFont，因此需要手动设置字体。
        app.option_add("*Menu.font", "TkMenuFont", "startupFile")
