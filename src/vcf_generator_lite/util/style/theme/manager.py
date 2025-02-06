import logging
from tkinter import Misc
from tkinter.font import nametofont
from tkinter.ttk import Style
from typing import Optional

from vcf_generator_lite.util.style.theme.config import ThemeConfig, ThemeColorName, ThemeTtkConfig

logger = logging.getLogger(__name__)


class ThemeManager:
    style: Style
    theme_config: ThemeConfig

    def __init__(self, master: Misc, theme_config: ThemeConfig):
        self.master = master
        self.theme_config = theme_config
        logger.info(f"Using tkinter theme: %s", self.theme_name)
        self.style = Style(master)
        self._on_apply_ttk_theme()
        self._on_apply_fonts()

    @property
    def theme_name(self) -> str:
        return self.theme_config["name"]

    @property
    def ttk_config(self) -> ThemeTtkConfig:
        return self.theme_config.get("ttk", {})

    @property
    def ttk_name(self) -> str:
        return self.ttk_config.get("name", "clam")

    @property
    def ttk_overrides(self) -> dict[str, dict[str, str]]:
        return self.ttk_config.get("overrides", {})

    @property
    def widgets_config(self):
        return self.theme_config.get("widgets", {})

    @property
    def colors_config(self):
        return self.theme_config.get("colors", {})

    def _parse_value(self, value: str) -> str:
        """
        解析包含特殊语法的字符串值，支持变量替换和样式查询功能。

        本方法用于处理以"$"开头的特殊值语法，支持以下两种格式的解析：
        1. 颜色变量替换："$color:<颜色名称>" 格式
        2. 样式配置查询："$lookup:<样式类型>:<选项名称>" 格式
        当值不符合上述格式时，直接返回原始字符串。
        """
        if isinstance(value, str) and value.startswith("$"):
            match value[1:].split(":"):
                case ("color", name):
                    return self.get_color(name)
                case ("lookup", style, option):
                    return self.style.lookup(style, option)
                case ("lookup", style, option, state):
                    return self.style.lookup(style, option, state.split(","))
                case ("map", style, option):
                    return self.style.map(style)[option]
        return value

    def _on_apply_ttk_theme(self):
        self.style.theme_use(self.ttk_name)
        for style, kwargs in self.ttk_overrides.items():
            self.style.configure(style, **kwargs)

        for widget, kwargs in self.widgets_config.items():
            for option, value in kwargs.items():
                self.master.option_add(f"*{widget}.{option}", self._parse_value(value), "widgetDefault")
        self.master["background"] = self.get_color("window_background")

    def _on_apply_fonts(self):
        font = nametofont("TkDefaultFont")
        font.config(size=12)
        font.config(**self.theme_config.get("fonts", {}).get("default", {}))
        self.master.option_add("*font", font, "widgetDefault")

    def get_color(self, key: ThemeColorName) -> Optional[str]:
        if value := self.colors_config.get(key):
            return self._parse_value(value)
        return None
