from tkinter import Misc


def tk_busy_hold(widget: Misc):
    if hasattr(widget, "tk_buy_hold"):
        # noinspection PyUnresolvedReferences
        widget.tk_busy_hold()  # pyright: ignore[reportAttributeAccessIssue, reportCallIssue]
    else:
        widget.tk.call("tk", "busy", "hold", str(widget))


def tk_busy_forget(widget: Misc):
    if hasattr(widget, "tk_busy_forget"):
        # noinspection PyUnresolvedReferences
        widget.tk_busy_forget()  # pyright: ignore[reportAttributeAccessIssue]
    else:
        widget.tk.call("tk", "busy", "forget", str(widget))


def tk_busy_status(widget: Misc) -> bool:
    if hasattr(widget, "tk_busy_status"):
        # noinspection PyUnresolvedReferences
        return widget.tk_busy_status()  # pyright: ignore
    else:
        return widget.tk.getboolean(widget.tk.call("tk", "busy", "status", str(widget)))
