from tkinter import Label, Event, Widget
from tkinter.ttk import Label as TtkLabel
from typing import Optional


def auto_wrap_configure_event(event: Event):
    widget = event.widget
    if isinstance(widget, Label) or isinstance(widget, TtkLabel):
        widget.configure(wraplength=event.width)


def update_padding(
    widget: Widget,
    *,
    left: Optional[int | str] = None,
    top: Optional[int | str] = None,
    right: Optional[int | str] = None,
    bottom: Optional[int | str] = None
):
    origin_padding = widget.cget("padding") or (0,)
    origin_left = origin_padding[0] if len(origin_padding) >= 1 else 0
    origin_top = origin_padding[1] if len(origin_padding) >= 2 else origin_left
    origin_right = origin_padding[1] if len(origin_padding) >= 2 else origin_left
    origin_bottom = origin_padding[1] if len(origin_padding) >= 2 else origin_top
    widget["padding"] = (
        left if left is not None else origin_left,
        top if top is not None else origin_top,
        right if right is not None else origin_right,
        bottom if bottom is not None else origin_bottom
    )
