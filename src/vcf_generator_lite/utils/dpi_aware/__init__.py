from vcf_generator_lite.utils.dpi_aware.base import DpiAware
from vcf_generator_lite.utils.environment import is_windows


def create_dpi_aware() -> DpiAware:
    if is_windows:
        from vcf_generator_lite.utils.dpi_aware.windows_impl import WindowsDpiAware

        return WindowsDpiAware()
    from vcf_generator_lite.utils.dpi_aware.null_impl import NullDpiAware

    return NullDpiAware()


_dpi_aware = create_dpi_aware()

enable_dpi_aware = _dpi_aware.enable_dpi_aware
