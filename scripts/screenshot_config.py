"""截图脚本共享的常量与语言设置。"""

import os

PLATFORM_NAMES = {"darwin": "macos", "linux": "linux"}
LANGUAGES = ("en-US", "zh-CN")
LOCALES = {"en-US": "en_US.UTF-8", "zh-CN": "zh_CN.UTF-8"}
# 统一用 CJK SC：单字体覆盖 U+26A0 警告符号 + Latin + 中文，两语种渲染逐像素一致，无需 hack。
# CJK SC 的 Latin 字形与 Noto Sans 几乎相同，英文截图观感可接受。
FONT_FAMILIES = {"en-US": "Noto Sans CJK SC", "zh-CN": "Noto Sans CJK SC"}


def set_language(lang: str) -> None:
    locale = LOCALES[lang]
    os.environ["LANGUAGE"] = locale
    os.environ["LC_ALL"] = locale
    os.environ["LANG"] = locale
