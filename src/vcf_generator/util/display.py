"""
大部分代码来自 https://github.com/TomSchimansky/CustomTkinter/blob/master/customtkinter/windows/widgets/scaling/scaling_tracker.py
"""
import sys
from tkinter import Misc

_default_dpi = 96
_process_dpi_aware = False


def _set_process_dpi_aware_win8_1():
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)  # PROCESS_SYSTEM_DPI_AWARE


def _set_process_dpi_aware_win7():
    from ctypes import windll
    windll.user32.SetProcessDPIAware()


# noinspection PyBroadException
def set_process_dpi_aware():
    """
    https://learn.microsoft.com/zh-cn/windows/win32/api/shellscalingapi/nf-shellscalingapi-setprocessdpiawareness
    """
    global _process_dpi_aware
    if sys.platform == 'win32':
        try:
            _set_process_dpi_aware_win8_1()
            _process_dpi_aware = True
        except Exception:
            try:
                _set_process_dpi_aware_win7()
                _process_dpi_aware = True
            except Exception:
                pass
    else:
        # 不支持缩放，忽略操作
        pass


def _get_scale_factor_win8_1(misc: Misc):
    from ctypes import windll, pointer, wintypes
    dpi_type = 0  # MDT_EFFECTIVE_DPI = 0, MDT_ANGULAR_DPI = 1, MDT_RAW_DPI = 2
    window_hwnd = wintypes.HWND(misc.winfo_id())
    monitor_handle = windll.user32.MonitorFromWindow(window_hwnd,
                                                     wintypes.DWORD(2))  # MONITOR_DEFAULTTONEAREST = 2
    dpi_x, dpi_y = wintypes.UINT(), wintypes.UINT()
    windll.shcore.GetDpiForMonitor(monitor_handle, dpi_type, pointer(dpi_x), pointer(dpi_y))
    return (dpi_x.value + dpi_y.value) / 2 / _default_dpi


def _get_scale_factor_win2000():
    from ctypes import windll, WinError, get_last_error
    hdc = windll.user32.GetDC(None)
    if not hdc:
        raise WinError(get_last_error())

    try:
        gdi32 = windll.gdi32
        dpi_x = gdi32.GetDeviceCaps(hdc, 88)  # LOGPIXELSX
        dpi_y = gdi32.GetDeviceCaps(hdc, 90)  # LOGPIXELSY
    finally:
        windll.user32.ReleaseDC(None, hdc)

    return (dpi_x + dpi_y) / 2 / _default_dpi


# noinspection PyBroadException
def get_scale_factor(misc: Misc) -> float:
    if not _process_dpi_aware:
        return 1.0
    if sys.platform == "win32":
        try:
            return _get_scale_factor_win8_1(misc)
        except Exception:
            try:
                return _get_scale_factor_win2000()
            except Exception:
                return 1.0

    else:
        # 不支持缩放，默认返回1
        return 1.0
