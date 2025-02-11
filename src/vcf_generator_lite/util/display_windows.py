"""
原始代码来源及版权声明:
https://github.com/TomSchimansky/CustomTkinter/blob/master/customtkinter/windows/widgets/scaling/scaling_tracker.py
License: MIT (https://github.com/TomSchimansky/CustomTkinter/blob/master/LICENSE)
"""

import logging
from contextlib import contextmanager
from ctypes import windll, pointer, WinError, get_last_error
from ctypes.wintypes import HWND, DWORD, UINT
from enum import Enum
from tkinter import Misc

DEFAULT_DPI = 96

MONITOR_DEFAULTTONEAREST = 2
LOGPIXELSX = 88
LOGPIXELSY = 90


class MonitorDpiType(Enum):
    """
    标识监视器 (dpi) 设置的每英寸点数。
    https://learn.microsoft.com/zh-cn/windows/win32/api/shellscalingapi/ne-shellscalingapi-monitor_dpi_type
    """

    MDT_EFFECTIVE_DPI = 0
    MDT_ANGULAR_DPI = 1
    MDT_RAW_DPI = 2


class ProcessDpiAwareness(Enum):
    """
    标识每英寸点数 (dpi) 感知值。 DPI 感知指示应用程序为 DPI 执行的缩放工作量与系统完成的缩放量。

    用户可以在其显示器上设置 DPI 比例系数，彼此独立。 某些旧版应用程序无法针对多个 DPI 设置调整其缩放比例。
    为了使用户能够使用这些应用程序，而不会在显示器上显示太大或太小的内容，Windows 可以将 DPI 虚拟化应用于应用程序，使系统自动缩放该应用程序以匹配当前显示器的 DPI。
    PROCESS_DPI_AWARENESS值指示应用程序自行处理的缩放级别以及 Windows 提供的缩放级别。
    请记住，系统缩放的应用程序可能看起来模糊，并且会读取有关监视器的虚拟化数据以保持兼容性。
    https://learn.microsoft.com/zh-cn/windows/win32/api/shellscalingapi/ne-shellscalingapi-process_dpi_awareness
    """

    PROCESS_DPI_UNAWARE = 0
    PROCESS_SYSTEM_DPI_AWARE = 1
    PROCESS_PER_MONITOR_DPI_AWARE = 2


@contextmanager
def get_dc(hwnd: HWND):
    hdc = windll.user32.GetDC(hwnd)
    if not hdc:
        raise WinError(get_last_error())
    try:
        yield hdc
    finally:
        windll.user32.ReleaseDC(hwnd, hdc)


def _enable_dpi_aware_win8_1():
    """
    https://learn.microsoft.com/zh-cn/windows/win32/api/shellscalingapi/nf-shellscalingapi-setprocessdpiawareness
    """
    result: int = windll.shcore.SetProcessDpiAwareness(ProcessDpiAwareness.PROCESS_SYSTEM_DPI_AWARE.value)
    if result != 0:
        raise WinError(get_last_error())


def _enable_dpi_aware_vista():
    """
    https://learn.microsoft.com/zh-cn/windows/win32/api/winuser/nf-winuser-setprocessdpiaware
    """
    result = bool(windll.user32.SetProcessDPIAware())
    if not result:
        raise WinError(get_last_error())


def enable_dpi_aware_windows():
    """
    设置进程默认 DPI 感知级别。

    该函数尝试将当前进程设置为 DPI 感知模式，以便在高 DPI 显示器上正确缩放。
    它针对不同的 Windows 版本尝试不同的设置方法。

    https://learn.microsoft.com/zh-cn/windows/win32/api/shellscalingapi/nf-shellscalingapi-setprocessdpiawareness
    """
    last_error = None

    for setter in (
        _enable_dpi_aware_win8_1,
        _enable_dpi_aware_vista,
    ):
        try:
            setter()
            break
        except (AttributeError, OSError) as e:
            last_error = e
            logging.debug(f"Failed to set process DPI awareness", exc_info=e)
    else:
        raise RuntimeError(last_error)


def _get_scale_factor_win10(misc: Misc) -> float:
    """
    https://learn.microsoft.com/zh-cn/windows/win32/api/winuser/nf-winuser-getdpiforwindow
    """

    return windll.user32.GetDpiForWindow(HWND(misc.winfo_id())) / DEFAULT_DPI


def _get_scale_factor_win8_1(misc: Misc) -> float:
    monitor_handle = windll.user32.MonitorFromWindow(
        HWND(misc.winfo_id()),
        DWORD(MONITOR_DEFAULTTONEAREST)
    )
    dpi_x, dpi_y = UINT(), UINT()
    windll.shcore.GetDpiForMonitor(
        monitor_handle,
        MonitorDpiType.MDT_EFFECTIVE_DPI.value,
        pointer(dpi_x),
        pointer(dpi_y),
    )

    return (dpi_x.value + dpi_y.value) / 2 / DEFAULT_DPI


def _get_scale_factor_win2000(misc: Misc) -> float:
    with get_dc(HWND(misc.winfo_id())) as hdc:
        dpi_x = windll.gdi32.GetDeviceCaps(hdc, LOGPIXELSX)
        dpi_y = windll.gdi32.GetDeviceCaps(hdc, LOGPIXELSY)

    return (dpi_x + dpi_y) / 2 / DEFAULT_DPI


def get_scale_factor_windows(misc: Misc) -> float:
    last_error = None
    for getter in (
        _get_scale_factor_win10,
        _get_scale_factor_win8_1,
        _get_scale_factor_win2000,
    ):
        try:
            return getter(misc)
        except (AttributeError, OSError) as e:
            last_error = e
            logging.debug(f"Failed to get scale factor", exc_info=e)
    else:
        raise RuntimeError(last_error)
