from vcf_generator_lite.utils.display.base import Display
from vcf_generator_lite.utils.environment import is_windows


def create_display() -> Display:
    if is_windows:
        from vcf_generator_lite.utils.display.windows_10_impl import Windows10Display
        return Windows10Display()
    else:
        from vcf_generator_lite.utils.display.null_impl import NullDisplay
        return NullDisplay()


_display = create_display()
get_default_scale_factor = _display.get_default_scale_factor
enable_dpi_aware = _display.enable_dpi_aware
