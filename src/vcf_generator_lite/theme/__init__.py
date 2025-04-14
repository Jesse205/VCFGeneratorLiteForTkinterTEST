from vcf_generator_lite.util.environment import is_windows
from vcf_generator_lite.util.tkinter.theme import Theme

__all__ = ["create_platform_theme"]


def create_platform_theme() -> Theme:
    if is_windows:
        from vcf_generator_lite.theme.widows_theme import WindowsTheme
        return WindowsTheme()

    from vcf_generator_lite.theme.clam_theme import ClamTheme
    return ClamTheme()
