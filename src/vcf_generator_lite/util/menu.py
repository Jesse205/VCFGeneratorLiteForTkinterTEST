from dataclasses import dataclass
from tkinter import Menu
from typing import Callable, Self, Optional, Literal


@dataclass
class MenuCommand:
    label: str
    command: Optional[Callable[[], object | str]] = None
    accelerator: Optional[str] = None
    state: Literal["normal", "active", "disabled"] = "normal"


@dataclass
class MenuSeparator:
    pass


@dataclass
class MenuCascade:
    label: str
    items: list[MenuCommand | MenuSeparator | Self]
    accelerator: Optional[str] = None
    tearoff: bool = False
    state: Literal["normal", "active", "disabled"] = "normal"


type MenuItem = MenuCommand | MenuSeparator | MenuCascade | type[MenuSeparator]


def _parse_label(label: str) -> tuple[str, int]:
    """
    解析标签字符串，将标签字符串中的快捷键标识符替换为对应的快捷键键值
    """
    return label.replace("&", "", 1), label.find("&")


def add_menu_items(menu: Menu, items: list[MenuItem]):
    """
    向给定的菜单对象中批量添加菜单项。
    """
    for item in items:
        if isinstance(item, MenuCommand):
            label, underline = _parse_label(item.label)
            menu.add_command(
                label=label,
                command=item.command,
                underline=underline,
                accelerator=item.accelerator,
                state=item.state,
            )
        elif isinstance(item, MenuSeparator):
            menu.add_separator()
        elif isinstance(item, MenuCascade):
            label, underline = _parse_label(item.label)
            submenu = Menu(menu, tearoff=item.tearoff)
            add_menu_items(submenu, item.items)
            menu.add_cascade(
                label=label,
                menu=submenu,
                underline=underline,
                accelerator=item.accelerator,
                state=item.state,
            )
