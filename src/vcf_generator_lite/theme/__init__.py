import logging
import sys
from typing import Optional

from vcf_generator_lite.util.style.theme import Theme

__all__ = ["get_platform_theme"]
logger = logging.getLogger(__name__)


def create_theme() -> Theme:
    if sys.platform == "win32":
        from vcf_generator_lite.theme.widows_theme import WindowsTheme
        return WindowsTheme()

    from vcf_generator_lite.theme.clam_theme import ClamTheme
    return ClamTheme()


_platform_theme: Optional[Theme] = None


def get_platform_theme() -> Theme:
    global _platform_theme
    if _platform_theme is None:
        _platform_theme = create_theme()
        logger.debug(f"Using {_platform_theme.__class__.__name__} theme")
    return _platform_theme
