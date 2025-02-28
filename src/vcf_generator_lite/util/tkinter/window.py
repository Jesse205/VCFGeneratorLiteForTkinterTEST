import re
from abc import ABC
from contextlib import contextmanager
from tkinter import Misc, Tk, Toplevel, Wm
from typing import Optional

from vcf_generator_lite.util.environment import is_windows

type Window = Tk | Toplevel


class WindowExtension(Misc, Wm, ABC):
    pass


type WindowOrExtension = Window | WindowExtension


def center_window(window: WindowOrExtension, parent: WindowOrExtension = None):
    window.update_idletasks()
    window_width = window.winfo_width()
    window_height = window.winfo_height()
    vroot_width = window.winfo_vrootwidth()
    vroot_height = window.winfo_vrootheight()
    vroot_x = window.winfo_vrootx()
    vroot_y = window.winfo_vrooty()
    window_max_x = vroot_x + vroot_width - window_width
    window_max_y = vroot_y + vroot_height - window_height
    if parent is not None:
        # 使用geometry获取包含窗口修饰的窗口位置
        match = re.match(r"(-?\d+)x(-?\d+)\+(-?\d+)\+(-?\d+)", parent.geometry())
        parent_x = int(match.group(3))
        parent_y = int(match.group(4))
        # 当窗口最大化时，geometry获取到的位置仍然是正常位置，所以要特殊判断
        if is_windows and parent.wm_state() == "zoomed":
            parent_x = window.winfo_vrootx()
            parent_y = window.winfo_vrooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        x = parent_x + (parent_width - window_width) // 2
        y = parent_y + (parent_height - window_height) // 2
    else:
        # maxsize不会包含任务栏高度，但是maxsize的值也会算上副屏，所以为了防止窗口超出当前屏幕，这里取最小值
        parent_maxsize = window.maxsize()
        parent_width = min(parent_maxsize[0], vroot_width)
        parent_height = min(parent_maxsize[1], vroot_height)
        x = (parent_width - window_width) // 2
        y = (parent_height - window_height) // 2
    x = max(min(x, window_max_x), vroot_x)
    y = max(min(y, window_max_y), vroot_y)
    window.geometry(f"+{x}+{y}")


class CenterWindowExtension(WindowExtension, ABC):

    def center(self, parent: WindowOrExtension = None):
        center_window(self, parent)


class ScalingWindowExtension(WindowExtension, ABC):
    _scale_factor: float = 1.0

    def __init__(self):
        self._scale_factor = self.scaling()

    def scaling(self, factor: Optional[float] = None):
        """
        设置或获取GUI缩放比例因子

        当传入factor参数时，设置当前缩放比例并应用新的缩放因子到Tkinter窗口。
        不传入参数时返回当前缩放比例因子。

        与 tk scaling ?-displayof window? ?number? 相同。
        """
        if factor is not None:
            self._scale_factor = factor
        return self.tk.call("tk", "scaling", factor)

    def get_scaled(self, value: int | float) -> int | float:
        if isinstance(value, int):
            return int(self._scale_factor * value)
        elif isinstance(value, float):
            return float(self._scale_factor * value)
        else:
            raise TypeError(f"{value} 必须为 int 或 float")

    def scale_kw(self, **kw: int | float):
        new_kw = {key: self.get_scaled(value) for key, value in kw.items()}
        return new_kw

    def scale_args(self, *args: int | float):
        new_args = [self.get_scaled(value) for value in args]
        return new_args


class GeometryWindowExtension(ScalingWindowExtension, WindowExtension, ABC):
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
