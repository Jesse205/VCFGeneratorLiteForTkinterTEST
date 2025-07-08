from vcf_generator_lite.utils.environment import is_windows
from vcf_generator_lite.utils.tkinter.theme import EnhancedTheme

__all__ = ["create_platform_theme"]


def create_platform_theme() -> EnhancedTheme:
    if is_windows:
        from vcf_generator_lite.themes.widows_theme import WindowsTheme

        return WindowsTheme()

    from vcf_generator_lite.themes.clam_theme import ClamTheme

    return ClamTheme()
