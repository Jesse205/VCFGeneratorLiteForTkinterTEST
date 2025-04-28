import gc
from abc import ABC
from contextlib import contextmanager
from functools import cached_property
from tkinter import Event, Misc, Tk, Toplevel, Wm
from typing import Literal

from vcf_generator_lite.util.graphics import Offset
from vcf_generator_lite.util.tkinter.misc import ScalingMiscExtension

type Window = Tk | Toplevel


class WindowExtension(Misc, Wm, ABC):
    pass


type WindowOrExtension = Window | WindowExtension


class GeometryOffsetWindowExtension(WindowExtension, ABC):
    def client_to_geometry_offset(self) -> Offset:
        return Offset(
            x=self.winfo_x() - self.winfo_rootx(),
            y=self.winfo_y() - self.winfo_rooty()
        )


class GeometryWindowExtension(ScalingMiscExtension, WindowExtension, ABC):
    def wm_size(self, width: int, height: int):
        self.wm_geometry(f"{width}x{height}")

    def wm_size_pt(self, width: int, height: int):
        """
        设置窗口大小
        注：窗口大小单位为虚拟像素
        """
        self.wm_size(*self.scale_args(width, height))

    def wm_minsize_pt(self, width: int, height: int):
        return self.wm_minsize(*self.scale_args(width, height))

    def wm_maxsize_pt(self, width: int, height: int):
        return self.wm_maxsize(*self.scale_args(width, height))


class GcWindowExtension(WindowExtension, ABC):
    def __init__(self):
        super().__init__()
        self.bind("<Destroy>", self._on_destroy, "+")

    def _on_destroy(self, event: Event):
        if event.widget == self:
            gc.collect()


type WindowingSystem = Literal["x11", "win32", "aqua"]


class WindowingSystemWindowExtension(WindowExtension, ABC):
    @cached_property
    def tk_windowing_system(self) -> WindowingSystem:
        return self.tk.call('tk', 'windowingsystem')


class CenterWindowExtension(GeometryOffsetWindowExtension, WindowExtension, ABC):

    def center_reference_rect(self, rect_x: int, rect_y: int, rect_width: int, rect_height: int):
        client_x_min = self.winfo_vrootx()
        client_x_max = client_x_min + self.winfo_vrootwidth() - self.winfo_width()
        client_y_min = self.winfo_vrooty()
        client_y_max = client_y_min + self.winfo_vrootheight() - self.winfo_height()
        client_x = rect_x + (rect_width - self.winfo_width()) // 2
        client_x = max(min(client_x, client_x_max), client_x_min)
        client_y = rect_y + (rect_height - self.winfo_height()) // 2
        client_y = max(min(client_y, client_y_max), client_y_min)
        # 在Windows上，winfo_x/y是窗口坐标，而winfo_rootx/y是工作区坐标，geometry接收窗口坐标，所以需要将工作区坐标转换为窗口坐标。
        geometry_offset = self.client_to_geometry_offset()
        window_x = client_x + geometry_offset.x
        window_y = client_y + geometry_offset.y
        self.geometry(f"+{window_x}+{window_y}")

    def center_reference_screen(self):
        self.center_reference_rect(
            rect_x=0,
            rect_y=0,
            rect_width=self.winfo_screenwidth(),
            rect_height=self.winfo_screenheight(),
        )

    def center_reference_master(self):
        self.center_reference_rect(
            rect_x=self.master.winfo_rootx(),
            rect_y=self.master.winfo_rooty(),
            rect_width=self.master.winfo_width(),
            rect_height=self.master.winfo_height(),
        )

    def center(self):
        if self.master is None:
            self.center_reference_screen()
        else:
            self.center_reference_master()


@contextmanager
def withdraw_cm(wm: Wm):
    """
    窗口隐藏上下文管理器

    专门解决 Tkinter 窗口初始化时因设置属性导致的闪烁问题。通过上下文管理器在初始化期间隐藏窗口，
    所有属性配置完成后再显示窗口，避免窗口在左上角短暂闪现的异常现象。
    """
    wm.wm_withdraw()
    yield
    wm.wm_deiconify()
