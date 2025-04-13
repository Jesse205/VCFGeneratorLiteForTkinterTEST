from vcf_generator_lite.util.display.null_impl import NullDisplay
from vcf_generator_lite.util.display.windows_10_impl import Windows10Display
from vcf_generator_lite.util.environment import is_windows

if is_windows:
    display = Windows10Display()
else:
    display = NullDisplay()

get_default_scale_factor = display.get_default_scale_factor
enable_dpi_aware = display.enable_dpi_aware
