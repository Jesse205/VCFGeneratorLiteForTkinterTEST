import sys

__all__ = ["platform_theme"]

from vcf_generator_lite.util.style.theme.config import ThemeConfig

platform_theme: ThemeConfig

if sys.platform == "win32":
    from vcf_generator_lite.theme.widows_theme import windows_theme as platform_theme
else:
    from vcf_generator_lite.theme.clam_theme import clam_theme as platform_theme
