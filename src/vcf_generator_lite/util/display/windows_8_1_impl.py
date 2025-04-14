import logging
from ctypes import WinError, get_last_error, pointer, windll
from ctypes.wintypes import DWORD, HWND, UINT
from enum import Enum
from tkinter import Misc

from vcf_generator_lite.util.display.windows_2000_impl import DEFAULT_DPI
from vcf_generator_lite.util.display.windows_vista_impl import WindowsVistaDisplay

MONITOR_DEFAULTTONEAREST = 2

_logger = logging.getLogger(__name__)


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


class Windows81Display(WindowsVistaDisplay):

    def get_default_scale_factor(self, misc: Misc) -> float:
        try:
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
        except (AttributeError, OSError) as e:
            _logger.warning(f"Failed to enable DPI awareness from Windows 8.1 API, fallback to Windows 2000 API.")
            _logger.warning(e)
            return super().get_default_scale_factor(misc)

    def enable_dpi_aware(self):
        try:
            result: int = windll.shcore.SetProcessDpiAwareness(ProcessDpiAwareness.PROCESS_SYSTEM_DPI_AWARE.value)
            if result != 0:
                raise WinError(get_last_error())
        except (AttributeError, OSError) as e:
            _logger.warning(f"Failed to enable DPI awareness from Windows 8.1 API, fallback to Windows Vista API.")
            _logger.warning(e)
            super().enable_dpi_aware()
