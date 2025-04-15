from tkinter import Misc

from vcf_generator_lite.util.display.base import Display


class NullDisplay(Display):
    def get_default_scale_factor(self, misc: Misc) -> float:
        return 1.0

    def enable_dpi_aware(self):
        pass
