import logging
from tkinter import *
import tkinter.font as tk_font
from tkinter.font import Font
from typing import Union

from vcf_generator.model.FontConfig import FontConfig
from vcf_generator.util import display
from vcf_generator.util.display import get_window_dpi_scaling
from vcf_generator.util.resource import get_window_icon

__all__ = ["BaseWindow"]

_default_font_list = [
    FontConfig("Microsoft YaHei UI", 9, "normal"),
    FontConfig("Microsoft YaHei", 9, "normal"),
    FontConfig("Segoe ui", 9, "normal"),
]


class WindowInjector(Misc, Wm):
    _dpi_scaling = 1

    def window_injector_init(self):
        self.withdraw()
        self._dpi_scaling = get_window_dpi_scaling(self)
        self._apply_default_icon()
        self._apply_default_font()
        self.on_init_widgets()
        menu_bar = Menu(self, tearoff=False)
        self.on_init_menus(menu_bar)
        if menu_bar.children:
            self.configure({"menu": menu_bar})
        self.center_window()
        self.deiconify()

    def _apply_default_icon(self):
        self.iconbitmap(default=get_window_icon())

    def _apply_default_font(self):
        families = tk_font.families(self)
        self.font = Font(self, size=10, weight=NORMAL)
        for font in _default_font_list:
            if font.family in families:
                self.font = Font(self, family=font.family, size=font.size, weight=font.weight)
                break
        self.option_add("*font", self.font)

    def on_init_widgets(self):
        pass

    def on_init_menus(self, menu_bar: Menu):
        pass

    def get_scaled(self, size: int):
        return int(size * self._dpi_scaling)

    def get_scaled_float(self, size: float):
        return size * self._dpi_scaling

    def set_size(self, width: int, height: int):
        """
        设置窗口大小
        注：窗口大小单位为虚拟像素
        """
        super().geometry(f"{self.get_scaled(width)}x{self.get_scaled(height)}")

    def set_minsize(self, width: int, height: int):
        super().minsize(self.get_scaled(width), self.get_scaled(height))

    def scale_values(self, **kw: Union[int, float]):
        new_kw = {}
        for key, value in kw.items():
            if isinstance(value, int):
                new_kw[key] = self.get_scaled(value)
            elif isinstance(value, float):
                new_kw[key] = self.get_scaled_float(value)
            else:
                raise TypeError(f"{key} 的值 {value} 必须为 int 或 float")
        return new_kw

    def center_window(self):

        self.update()
        window_width = self.winfo_width()
        window_height = self.winfo_height()
        # maxsize不会包含任务栏高度，但是maxsize的值也会算上副屏，所以为了防止窗口超出当前屏幕，这里取最小值
        max_width, max_height = self.maxsize()
        container_width = min(max_width, self.winfo_screenwidth())
        container_height = min(max_height, self.winfo_screenheight())
        logging.info(
            f"Container size: {container_width}x{container_height}, window size: {window_width}x{window_height}")
        location_x = max(int((container_width - window_width) / 2), 0)
        location_y = max(int((container_height - window_height) / 2), 0)
        self.geometry(f"{window_width}x{window_height}+{location_x}+{location_y}")


class BaseWindow(Tk, WindowInjector):
    def __init__(self, screenName=None, baseName=None, className="Tk", useTk=True, sync=False, use=None):
        super().__init__(screenName, baseName, className, useTk, sync, use)
        self.window_injector_init()


class BaseToplevel(Toplevel, WindowInjector):
    def __init__(self, master=None, cnf={}, **kw):
        super().__init__(master, cnf, **kw)
        self.window_injector_init()
