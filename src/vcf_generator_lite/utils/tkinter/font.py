from tkinter.font import nametofont
from typing import Literal, TypedDict


class FontConfig(TypedDict, total=False):
    family: str
    size: int
    weight: Literal["normal", "bold"]
    slant: Literal["roman", "italic"]
    underline: bool
    overstrike: bool


def extend_font_scale(origin_name: str, scale: float):
    font = nametofont(origin_name).copy()
    font.configure(size=round(int(font.actual("size")) * scale))
    return font
