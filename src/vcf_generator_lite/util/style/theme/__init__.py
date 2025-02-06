from tkinter import Misc

from vcf_generator_lite.theme.platform_theme import platform_theme
from vcf_generator_lite.util.style.theme.manager import ThemeManager

_theme_manager = None


def get_theme_manager(master: Misc) -> ThemeManager:
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager(master, platform_theme)
    return _theme_manager
