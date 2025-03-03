from tkinter import Misc
from tkinter.font import nametofont
from tkinter.ttk import Style
from typing import override

from vcf_generator_lite.theme.base import BaseTheme


class WindowsTheme(BaseTheme):
    @override
    def apply_theme(self, master: Misc, style: Style):
        super().apply_theme(master, style)
        style.theme_use("vista")

        # 重写部分配置以适配高分屏
        style.configure("TButton", padding="2.5p")
        style.configure("Treeview", rowheight="15p")
        style.configure("Heading", padding="1.5p")

        # 自定义组件
        style.configure("TextFrame.TEntry", padding=0, borderwidth="1.5p", bordercolor="SystemHighlight")
        style.configure("InfoHeader.TFrame", background="systemWindow")
        style.configure("InfoHeaderContent.TFrame", background="systemWindow")
        style.configure("InfoHeaderContent.TLabel", background="systemWindow")

        # Windows 7 中菜单默认不使用TkMenuFont，因此需要手动设置字体。
        menu_font = nametofont("TkMenuFont")
        master.option_add("*Menu.font", menu_font)
