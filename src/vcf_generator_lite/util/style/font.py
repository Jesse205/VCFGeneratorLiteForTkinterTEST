from tkinter.font import nametofont
from typing import TypedDict, Literal
from typing import Unpack


class FontConfig(TypedDict, total=False):
    family: str
    size: int
    weight: Literal["normal", "bold"]
    slant: Literal["roman", "italic"]
    underline: bool
    overstrike: bool


def extend_font(origin_name: str, **options: Unpack[FontConfig]):
    font = nametofont(origin_name).copy()
    font.config(**options)
    return font
