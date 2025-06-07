from tkinter import Tk, Toplevel
from tkinter.font import nametofont
from tkinter.ttk import Style
from typing import override

from vcf_generator_lite.theme.base import BaseTheme


class ClamTheme(BaseTheme):
    @override
    def apply_tk(self, master: Tk, style: Style):
        super().apply_tk(master, style)
        style.theme_use("clam")
        default_font = nametofont("TkDefaultFont")
        default_font_size = int(default_font.actual("size"))

        # 重写部分配置以适配高分屏
        style.configure("TButton", padding="2.5p")
        style.configure("Treeview", rowheight=f"{default_font_size + 6}p")
        style.configure("Heading", padding="2.25p")
        style.configure("Vertical.TScrollbar", arrowsize="9p")

        # 自定义组件
        style.configure("DialogHeader.TFrame", relief="raised")
        style.configure("ThemedText.TEntry", padding=0, borderwidth="1.5p")

    @override
    def apply_window(self, master: Tk | Toplevel, style: Style):
        super().apply_window(master, style)
        # 窗口背景色不会跟随主题变化，需要手动设置
        window_background = style.lookup("TFrame", "background")
        master.configure(background=window_background)
