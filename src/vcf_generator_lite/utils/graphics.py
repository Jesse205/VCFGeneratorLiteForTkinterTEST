from dataclasses import dataclass
from tkinter import Misc
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from collections.abc import Sequence


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
        return self.left, self.top, self.right, self.bottom


def parse_ttk_padding(master: Misc, value: str | float | tuple[str | int | float, ...]) -> FPixelPadding:
    if isinstance(value, (int, float)):
        return FPixelPadding(value, value, value, value)

    parts: Sequence[str | int | float] = value.split() if isinstance(value, str) else value
    padding = (*map(master.winfo_fpixels, parts), None, None, None, None)

    left = padding[0] if padding[0] is not None else 0
    top = padding[1] if padding[1] is not None else left
    right = padding[2] if padding[2] is not None else left
    bottom = padding[3] if padding[3] is not None else top
    return FPixelPadding(left, top, right, bottom)
