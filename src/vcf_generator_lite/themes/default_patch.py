from tkinter import Tk
from tkinter.font import nametofont
from typing import override

from vcf_generator_lite.themes.base import BaseThemePatch


class DefaultThemePatch(BaseThemePatch):
    @override
    def __init__(self, app: Tk):
        super().__init__(app)

        treeview_font = nametofont(self.style.lookup("Treeview", "font", default="TkDefaultFont"))
        treeview_font_metrics = treeview_font.metrics()

        # 重写部分配置以适配高分屏
        self.style.configure("TButton", padding="2.5p", width=-8)
        self.style.configure("Treeview", rowheight=treeview_font_metrics.get("linespace") + app.winfo_pixels("2.5p"))
        self.style.configure("Heading", padding="2.25p")
        self.style.configure("Vertical.TScrollbar", arrowsize="9p")
