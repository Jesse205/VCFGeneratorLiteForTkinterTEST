from typing import TypedDict, Literal, Required

from vcf_generator_lite.util.style.font import FontConfig


class ThemeTtkConfig(TypedDict, total=False):
    name: str
    overrides: dict[str, dict[str, str]]


class ThemeColors(TypedDict, total=False):
    window_background: str
    highlight_background: str
    highlight_foreground: str
    tooltip_background: str
    tooltip_foreground: str
    client_background: str
    client_foreground: str


type ThemeColorName = Literal[
    "window_background",
    "highlight_background",
    "highlight_foreground",
    "tooltip_background",
    "tooltip_foreground",
    "client_background",
    "client_foreground",
]


class ThemeFonts(TypedDict, total=False):
    default: str | FontConfig


type ThemeFontName = Literal["default"]


class ThemeConfig(TypedDict, total=False):
    name: Required[str]
    ttk: ThemeTtkConfig
    colors: ThemeColors
    fonts: ThemeFonts
    widgets: dict[str, dict[str, str]]
