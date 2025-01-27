import logging
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


_process_dpi_aware = False


def _set_process_dpi_aware_win8_1():
    """
    https://learn.microsoft.com/zh-cn/windows/win32/api/shellscalingapi/nf-shellscalingapi-setprocessdpiawareness
    """
    windll.shcore.SetProcessDpiAwareness(ProcessDpiAwareness.PROCESS_SYSTEM_DPI_AWARE.value)


def _set_process_dpi_aware_win_vista():
    """
    https://learn.microsoft.com/zh-cn/windows/win32/api/winuser/nf-winuser-setprocessdpiaware
    """
    windll.user32.SetProcessDPIAware()


def set_process_dpi_aware():
    """
    设置进程默认 DPI 感知级别。

    该函数尝试将当前进程设置为 DPI 感知模式，以便在高 DPI 显示器上正确缩放。
    它针对不同的 Windows 版本尝试不同的设置方法。如果在所有尝试均失败或在非 Windows 平台上运行，
    则该函数不会产生任何影响。

    https://learn.microsoft.com/zh-cn/windows/win32/api/shellscalingapi/nf-shellscalingapi-setprocessdpiawareness
    """
    global _process_dpi_aware

    for setter in (
        _set_process_dpi_aware_win8_1,
        _set_process_dpi_aware_win_vista,
    ):
        try:
            setter()
        except (AttributeError, OSError) as e:
            logging.debug(f"Failed to set process DPI awareness",exc_info=e)
        else:
            _process_dpi_aware = True
            break


def _get_scale_factor_win10(misc: Misc) -> float:
    """
    https://learn.microsoft.com/zh-cn/windows/win32/api/winuser/nf-winuser-getdpiforwindow
    """
    hwnd = HWND(misc.winfo_id())
    return windll.user32.GetDpiForWindow(hwnd) / DEFAULT_DPI


def _get_scale_factor_win8_1(misc: Misc) -> float:
    shcore = windll.shcore
    user32 = windll.user32
    hwnd = HWND(misc.winfo_id())
    monitor_handle = user32.MonitorFromWindow(hwnd, DWORD(MONITOR_DEFAULTTONEAREST))
    dpi_x, dpi_y = UINT(), UINT()
    shcore.GetDpiForMonitor(monitor_handle, MonitorDpiType.MDT_EFFECTIVE_DPI.value, pointer(dpi_x), pointer(dpi_y))

    return (dpi_x.value + dpi_y.value) / 2 / DEFAULT_DPI


def _get_scale_factor_win2000() -> float:
    gdi32 = windll.gdi32
    user32 = windll.user32

    hdc = user32.GetDC(None)
    if not hdc:
        raise WinError(get_last_error())

    try:
        dpi_x = gdi32.GetDeviceCaps(hdc, LOGPIXELSX)
        dpi_y = gdi32.GetDeviceCaps(hdc, LOGPIXELSY)
    finally:
        user32.ReleaseDC(None, hdc)

    return (dpi_x + dpi_y) / 2 / DEFAULT_DPI


def get_scale_factor(misc: Misc) -> float:
    """
    获取缩放因子。

    在不同操作系统上获取缩放因子，以便在高 DPI 屏幕上正确显示界面。
    缩放因子影响如何将逻辑坐标转换为屏幕坐标。

    :param misc: Misc对象
    :return: 缩放因子，如果无法确定则默认返回 1.0。
    """
    if not _process_dpi_aware:
        return 1.0

    for getter in (
        lambda: _get_scale_factor_win10(misc),
        lambda: _get_scale_factor_win8_1(misc),
        _get_scale_factor_win2000,
    ):
        try:
            return getter()
        except (AttributeError, OSError) as e:
            logging.debug(f"Failed to get scale factor", exc_info=e)

    # 不支持缩放，默认返回1
    return 1.0
