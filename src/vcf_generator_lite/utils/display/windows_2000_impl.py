from abc import ABC
from contextlib import contextmanager
from ctypes import WinError, get_last_error, windll
from ctypes.wintypes import HWND
from tkinter import Misc

from vcf_generator_lite.utils.display.base import Display

LOGPIXELSX = 88
LOGPIXELSY = 90

DEFAULT_DPI = 96


@contextmanager
def get_dc(hwnd: HWND):
    hdc = windll.user32.GetDC(hwnd)
    if not hdc:
        raise WinError(get_last_error())
    try:
        yield hdc
    finally:
        windll.user32.ReleaseDC(hwnd, hdc)


class Windows2000Display(Display, ABC):
    @staticmethod
    def get_default_scale_factor(misc: Misc) -> float:
        with get_dc(HWND(misc.winfo_id())) as hdc:
            dpi_x = windll.gdi32.GetDeviceCaps(hdc, LOGPIXELSX)
            dpi_y = windll.gdi32.GetDeviceCaps(hdc, LOGPIXELSY)

        return (dpi_x + dpi_y) / 2 / DEFAULT_DPI
