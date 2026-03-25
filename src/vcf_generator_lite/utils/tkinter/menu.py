from typing import TypedDict


class ParseLabelResult(TypedDict):
    label: str
    underline: int


def parse_menu_label(label: str) -> ParseLabelResult:
    """解析标签字符串，将标签字符串中的快捷键标识符设置为对应的快捷键键值"""
    return ParseLabelResult(label=label.replace("&", "", 1), underline=label.find("&"))
