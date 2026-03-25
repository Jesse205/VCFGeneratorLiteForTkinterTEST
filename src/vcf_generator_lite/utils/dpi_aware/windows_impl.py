import logging
from ctypes import FormatError, get_last_error, windll
from enum import Enum
from typing import override

from vcf_generator_lite.utils.dpi_aware.base import DpiAware

logger = logging.getLogger(__name__)


class ProcessDpiAwareness(Enum):
    """详情请参阅 https://learn.microsoft.com/zh-cn/windows/win32/api/shellscalingapi/ne-shellscalingapi-process_dpi_awareness。"""

    PROCESS_DPI_UNAWARE = 0
    PROCESS_SYSTEM_DPI_AWARE = 1
    PROCESS_PER_MONITOR_DPI_AWARE = 2


class WindowsDpiAware(DpiAware):
    @override
    @staticmethod
    def enable_dpi_aware() -> bool:
        if WindowsDpiAware._try_set_process_dpi_awareness():
            return True
        return WindowsDpiAware._try_set_process_dpi_aware()

    @staticmethod
    def _try_set_process_dpi_awareness() -> bool:
        """从 Windows 8.1 开始。详情请参阅 https://learn.microsoft.com/zh-cn/windows/win32/api/shellscalingapi/nf-shellscalingapi-setprocessdpiawareness。"""
        if not hasattr(windll.shcore, "SetProcessDpiAwareness"):
            return False
        result: int = windll.shcore.SetProcessDpiAwareness(ProcessDpiAwareness.PROCESS_SYSTEM_DPI_AWARE.value)
        if result != 0:
            logger.warning("Failed to call SetProcessDpiAwareness: %s", FormatError(get_last_error()))
        return result == 0

    @staticmethod
    def _try_set_process_dpi_aware() -> bool:
        """从 Windows Vista 开始。详情请查阅 https://learn.microsoft.com/zh-cn/windows/win32/api/winuser/nf-winuser-setprocessdpiaware。"""
        if not hasattr(windll.user32, "SetProcessDPIAware"):
            return False
        result = bool(windll.user32.SetProcessDPIAware())
        if not result:
            logger.warning("Failed to call SetProcessDPIAware: %s", FormatError(get_last_error()))
        return result
