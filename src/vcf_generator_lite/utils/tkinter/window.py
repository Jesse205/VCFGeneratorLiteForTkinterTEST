from abc import ABC
from contextlib import contextmanager
from tkinter import Misc, Tk, Toplevel, Wm

from vcf_generator_lite.utils.graphics import Offset
from vcf_generator_lite.utils.tkinter.misc import scale_args

type Window = Tk | Toplevel


class WindowExtension(Misc, Wm, ABC):
    """窗口方法扩展基类"""


type WindowOrExtension = Window | WindowExtension


class GeometryWindowExtension(WindowExtension, ABC):
    """带缩放的窗口尺寸方法扩展"""

    def wm_size(self, width: int, height: int):
        self.wm_geometry(f"{width}x{height}")

    def wm_size_pt(self, width: int, height: int):
        self.wm_size(*scale_args(self, width, height))

    def wm_minsize_pt(self, width: int, height: int) -> None:
        return self.wm_minsize(*scale_args(self, width, height))

    def wm_maxsize_pt(self, width: int, height: int) -> None:
        return self.wm_maxsize(*scale_args(self, width, height))


def get_client_to_geometry_offset(window: Misc) -> Offset:
    return Offset(x=window.winfo_x() - window.winfo_rootx(), y=window.winfo_y() - window.winfo_rooty())


class CenterWindowExtension(WindowExtension, ABC):
    def center_reference_rect(self, rect_x: int, rect_y: int, rect_width: int, rect_height: int):
        client_x_min = self.winfo_vrootx()
        client_x_max = client_x_min + self.winfo_vrootwidth() - self.winfo_width()
        client_y_min = self.winfo_vrooty()
        client_y_max = client_y_min + self.winfo_vrootheight() - self.winfo_height()
        if self._windowingsystem == "aqua":
            client_y_min = max(client_y_min, 22)

        client_x = rect_x + (rect_width - self.winfo_width()) // 2
        client_x = max(min(client_x, client_x_max), client_x_min)
        client_y = rect_y + (rect_height - self.winfo_height()) // 2
        client_y = max(min(client_y, client_y_max), client_y_min)
        # 在 Windows 上，winfo_x/y 是窗口坐标，而 winfo_rootx/y 是工作区坐标，geometry 接收窗口坐标，
        # 所以需要将工作区坐标转换为窗口坐标。
        geometry_offset = get_client_to_geometry_offset(self)
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
        if self.master is None:
            msg = "master is None"
            raise ValueError(msg)
        self.center_reference_rect(
            rect_x=self.master.winfo_rootx(),
            rect_y=self.master.winfo_rooty(),
            rect_width=self.master.winfo_width(),
            rect_height=self.master.winfo_height(),
        )

    def center(self):
        """如果 `master` 为 `None`，则居中于屏幕；否则居中于 master 窗口。"""
        if self.master is None:
            self.center_reference_screen()
        else:
            self.center_reference_master()


@contextmanager
def withdraw_cm(wm: Wm):
    """窗口隐藏上下文管理器。

    专门解决 Tkinter 窗口初始化时因设置属性导致的闪烁问题。通过上下文管理器在初始化期间隐藏窗口，
    所有属性配置完成后再显示窗口，避免窗口在左上角短暂闪现的异常现象。
    """
    wm.wm_withdraw()
    yield
    wm.wm_deiconify()
