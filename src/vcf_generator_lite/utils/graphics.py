from dataclasses import dataclass
from tkinter import Misc
from typing import NamedTuple


class Offset(NamedTuple):
    x: int
    y: int


@dataclass(frozen=True)
class FPixelPadding:
    left: float = 0
    top: float = 0
    right: float = 0
    bottom: float = 0

    def __add__(self, other: "FPixelPadding") -> "FPixelPadding":
        """合并四周边距"""
        return FPixelPadding(
            left=self.left + other.left,
            top=self.top + other.top,
            right=self.right + other.right,
            bottom=self.bottom + other.bottom,
        )

    def __sub__(self, other: "FPixelPadding") -> "FPixelPadding":
        """减去四周边距"""
        return FPixelPadding(
            left=self.left - other.left,
            top=self.top - other.top,
            right=self.right - other.right,
            bottom=self.bottom - other.bottom,
        )

    def to_tuple(self) -> tuple[float, float, float, float]:
        return (self.left, self.top, self.right, self.bottom)


def parse_padding(master: Misc, value: str | float | tuple[str | int | float, ...]) -> FPixelPadding:
    padding = value
    if isinstance(padding, str):
        padding = padding.split()
    elif isinstance(padding, (int, float)):
        padding = (padding,)
    left = master.winfo_fpixels(str(padding[0])) if len(padding) >= 1 else 0
    top = master.winfo_fpixels(str(padding[1])) if len(padding) >= 2 else left
    right = master.winfo_fpixels(str(padding[2])) if len(padding) >= 3 else left
    bottom = master.winfo_fpixels(str(padding[3])) if len(padding) >= 4 else top
    return FPixelPadding(left, top, right, bottom)
