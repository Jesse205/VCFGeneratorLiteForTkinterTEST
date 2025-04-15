from tkinter import Misc

from vcf_generator_lite.util.display.base import Display


class NullDisplay(Display):
    @staticmethod
    def get_default_scale_factor(misc: Misc) -> float:
        return 1.0

    @staticmethod
    def enable_dpi_aware():
        pass
