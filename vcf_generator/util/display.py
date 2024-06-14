"""
大部分代码来自 https://github.com/TomSchimansky/CustomTkinter/blob/master/customtkinter/windows/widgets/scaling/scaling_tracker.py
"""
import ctypes
import os
import sys
from enum import Enum
from tkinter import Misc


class WinDpiAwareness(Enum):
    """
    标识每英寸点数 (dpi) 感知值。 DPI 感知指示应用程序为 DPI 执行的缩放工作量与系统完成的缩放量。

    用户可以在其显示器上设置 DPI 比例系数，彼此独立。某些旧版应用程序无法针对多个 DPI 设置调整其缩放比例。
    为了使用户能够使用这些应用程序，而不会在显示器上显示太大或太小的内容，Windows 可以将 DPI 虚拟化应用于应用程序，使系统自动缩放该应用程序以匹配当前显示器的 DPI。
    PROCESS_DPI_AWARENESS值指示应用程序自行处理的缩放级别以及 Windows 提供的缩放级别。
    请记住，系统缩放的应用程序可能看起来模糊，并且会读取有关监视器的虚拟化数据以保持兼容性。

    https://learn.microsoft.com/zh-cn/windows/win32/api/shellscalingapi/ne-shellscalingapi-process_dpi_awareness
    """

    PROCESS_DPI_UNAWARE = 0
    """
    DPI 不知道。 此应用不会缩放 DPI 更改，并且始终假定其比例系数为 100% (96 DPI) 。 系统将在任何其他 DPI 设置上自动缩放它。
    """
    PROCESS_SYSTEM_DPI_AWARE = 1
    """
    系统 DPI 感知。 此应用不会缩放 DPI 更改。 它将查询 DPI 一次，并在应用的生存期内使用该值。
    如果 DPI 发生更改，应用将不会调整为新的 DPI 值。 当 DPI 与系统值发生更改时，系统会自动纵向扩展或缩减它。
    """
    PROCESS_PER_MONITOR_DPI_AWARE = 2
    """
    按监视器 DPI 感知。
    此应用在创建 DPI 时检查 DPI，并在 DPI 发生更改时调整比例系数。
    系统不会自动缩放这些应用程序。
    """


def set_process_dpi_aware(value: WinDpiAwareness):
    """
    https://learn.microsoft.com/zh-cn/windows/win32/api/shellscalingapi/nf-shellscalingapi-setprocessdpiawareness
    """
    if not sys.platform == 'win32':
        return
    # noinspection PyBroadException
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(value.value)
    except Exception:
        pass


def get_window_dpi_scaling(misc: Misc) -> float:
    if sys.platform == "win32":
        from ctypes import windll, pointer, wintypes
        # noinspection PyBroadException
        try:
            dpi100pc = 96  # DPI 96 is 100% scaling
            dpi_type = 0  # MDT_EFFECTIVE_DPI = 0, MDT_ANGULAR_DPI = 1, MDT_RAW_DPI = 2
            window_hwnd = wintypes.HWND(misc.winfo_id())
            monitor_handle = windll.user32.MonitorFromWindow(window_hwnd,
                                                             wintypes.DWORD(2))  # MONITOR_DEFAULTTONEAREST = 2
            x_dpi, y_dpi = wintypes.UINT(), wintypes.UINT()
            windll.shcore.GetDpiForMonitor(monitor_handle, dpi_type, pointer(x_dpi), pointer(y_dpi))
            return (x_dpi.value + y_dpi.value) / (2 * dpi100pc)
        except Exception:
            return 1
    return 1
