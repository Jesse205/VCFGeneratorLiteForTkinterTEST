import logging
import sys
from tkinter import *
from typing import Union, Optional

from vcf_generator_lite.theme import get_platform_theme
from vcf_generator_lite.util.display import get_scale_factor
from vcf_generator_lite.util.menu import add_menu_items, MenuItem
from vcf_generator_lite.util.resource import get_asset_data

__all__ = ["BaseWindow", "BaseToplevel", "BaseDialog"]

logger = logging.getLogger(__name__)

EVENT_EXIT = "<<Exit>>"


class WindowExtension(Misc, Wm):
    _scale_factor = 1
    menu_bar: Optional[Menu] = None

    def on_init_window(self):
        pass

    def window_injector_init(self):
        self.withdraw()
        self.__apply_default_scaling()
        self.__apply_default_icon()
        self.__apply_default_events()

        self.on_init_window()
        self.center_window()
        # 延迟0秒调用center_window，修复WSL中窗口大小获取不正确
        # after_idle不起作用
        if sys.platform == "linux":
            self.after(0, self.center_window)
        self.deiconify()

    def __apply_default_scaling(self):
        self._scale_factor = get_scale_factor(self)
        self.tk.call("tk", "scaling", self._scale_factor)

    def __apply_default_icon(self):
        logger.debug(f"窗口 {self.winfo_name()} 设置图标为 icon-48.png")
        self.iconphoto(True, PhotoImage(data=get_asset_data("images/icon-48.png")))

    def __apply_default_events(self):
        self.protocol("WM_DELETE_WINDOW", lambda: self.event_generate(EVENT_EXIT))
        self.bind(EVENT_EXIT, lambda _: self.destroy())

    def get_scaled(self, size: int):
        return int(size * self._scale_factor)

    def get_scaled_float(self, size: float):
        return size * self._scale_factor

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
        self.update_idletasks()
        window_width = self.winfo_width()
        window_height = self.winfo_height()
        # maxsize不会包含任务栏高度，但是maxsize的值也会算上副屏，所以为了防止窗口超出当前屏幕，这里取最小值
        max_width, max_height = self.maxsize()
        container_width = min(max_width, self.winfo_screenwidth())
        container_height = min(max_height, self.winfo_screenheight())
        location_x = max(int((container_width - window_width) / 2), 0)
        location_y = max(int((container_height - window_height) / 2), 0)
        self.geometry(f"+{location_x}+{location_y}")

    def add_menu_bar_items(self, *items: MenuItem):
        if self.menu_bar is None:
            self.menu_bar = Menu(self, tearoff=False)
            self.configure({"menu": self.menu_bar})
        add_menu_items(self.menu_bar, list(items))


class BaseWindow(Tk, WindowExtension):
    def __init__(self, screenName=None, baseName=None, className="Tk", useTk=True, sync=False, use=None):
        super().__init__(screenName, baseName, className, useTk, sync, use)
        get_platform_theme().apply_theme(self)
        self.window_injector_init()


class BaseToplevel(Toplevel, WindowExtension):
    def __init__(self, master=None, cnf={}, **kw):
        super().__init__(master, cnf, **kw)
        self.window_injector_init()


class BaseDialog(BaseToplevel):
    def on_init_window(self):
        self.bind("<Escape>", lambda _: self.event_generate(EVENT_EXIT))

        if isinstance(self.master, Wm):
            self.transient(self.master)
            self.resizable(False, False)
