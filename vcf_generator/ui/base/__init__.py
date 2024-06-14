import os
from tkinter import *
import tkinter.font as tk_font
from vcf_generator.util import display
from vcf_generator.util.display import get_window_dpi_scaling

__all__ = ["BaseWindow"]

_default_font_list = [
    ("Microsoft YaHei UI", 9)
]
_default_icon_list = ["./assets/icon.ico", "./_internal/assets/icon.ico"]

display.set_process_dpi_aware(display.WinDpiAwareness.PROCESS_SYSTEM_DPI_AWARE)


class BaseWindow(Tk):
    def __init__(self, screen_name=None, base_name=None, class_name='Tk',
                 use_tk=True, sync=False, use=None):
        super().__init__(screen_name, base_name, class_name, use_tk, sync, use)
        self.withdraw()
        self._dpi_scaling = get_window_dpi_scaling(self)
        self._apply_default_icon()
        self._apply_default_font()
        self.on_init_widgets()
        menu_bar = Menu(self, tearoff=False)
        self.on_init_menus(menu_bar)
        if menu_bar.children:
            self.config(menu=menu_bar)
        self.deiconify()

    def _apply_default_icon(self):
        for icon_path in _default_icon_list:
            if os.path.exists(icon_path):
                self.iconbitmap(default=icon_path)

    def _apply_default_font(self):
        families = tk_font.families(self)
        for font in _default_font_list:
            if font[0] in families:
                self.option_add("*font", font)
                break

    def on_init_widgets(self):
        pass

    def on_init_menus(self, menu_bar: Menu):
        pass

    def get_scaled(self, size: int):
        return int(size * self._dpi_scaling)

    def get_scaled_float(self, size: float):
        return size * self._dpi_scaling

    def set_size(self, width: int, height: int):
        super().geometry(f"{self.get_scaled(width)}x{self.get_scaled(height)}")

    def set_minsize(self, width: int, height: int):
        super().minsize(self.get_scaled(width), self.get_scaled(height))

    def pack_widget(self, widget: Widget, **kw):
        """
        适配了缩放的 pack 方法，pady 与 padx 现在为虚拟像素。
        """
        if "pady" in kw:
            kw["pady"] = self.get_scaled_float(kw["pady"])
        if "padx" in kw:
            kw["padx"] = self.get_scaled_float(kw["padx"])
        widget.pack(**kw)
