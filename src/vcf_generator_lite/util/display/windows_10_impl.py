import logging
from ctypes import windll
from ctypes.wintypes import HWND
from tkinter import Misc

from vcf_generator_lite.util.display.windows_2000_impl import DEFAULT_DPI
from vcf_generator_lite.util.display.windows_8_1_impl import Windows81Display

_logger = logging.getLogger(__name__)


class Windows10Display(Windows81Display):
    def get_default_scale_factor(self, misc: Misc) -> float:
        try:
            return windll.user32.GetDpiForWindow(HWND(misc.winfo_id())) / DEFAULT_DPI
        except (AttributeError, OSError) as e:
            _logger.warning("Failed to get scale factor from Windows 10 API, fallback to Windows 8.1 API", exc_info=e)
            return super().get_default_scale_factor(misc)
