from tkinter import Tk
from tkinter.font import nametofont
from tkinter.ttk import Style
from typing import override

from vcf_generator_lite.theme.base import BaseTheme


class WindowsTheme(BaseTheme):
    @override
    def apply_tk(self, master: Tk, style: Style):
        super().apply_tk(master, style)
        style.theme_use("vista")
        default_font = nametofont("TkDefaultFont")
        default_font_size = int(default_font.actual("size"))

        # 重写部分配置以适配高分屏
        style.configure("TButton", padding="2.5p")
        style.configure("Treeview", rowheight=f"{default_font_size + 6}p")
        style.configure("Heading", padding="1.5p")

        # 自定义组件
        style.configure("ThemedText.TEntry", padding=0, borderwidth="1.5p", bordercolor="SystemHighlight")
        style.configure("DialogHeader.TFrame", background="systemWindow")
        style.configure("DialogHeaderContent.TFrame", background="systemWindow")
        style.configure("DialogHeaderContent.TLabel", background="systemWindow")

        # Windows 7 中菜单默认不使用TkMenuFont，因此需要手动设置字体。
        menu_font = nametofont("TkMenuFont")
        master.option_add("*Menu.font", menu_font, "startupFile")
