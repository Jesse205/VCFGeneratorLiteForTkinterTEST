"""截图脚本共享的常量与语言设置。"""

import os

PLATFORM_NAMES = {"darwin": "macos", "linux": "linux"}
LANGUAGES = ("en-US", "zh-CN")
LOCALES = {"en-US": "en_US.UTF-8", "zh-CN": "zh_CN.UTF-8"}
FONT_FAMILIES = {"en-US": "Noto Sans", "zh-CN": "Noto Sans CJK SC"}


def set_language(lang: str) -> None:
    locale = LOCALES[lang]
    os.environ["LANGUAGE"] = locale
    os.environ["LC_ALL"] = locale
    os.environ["LANG"] = locale
