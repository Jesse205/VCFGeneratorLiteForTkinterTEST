import logging
from tkinter import Misc, Tk
from typing import Any, overload

ATTR_SCALING_CACHED = "_scaling_cached"

logger = logging.getLogger(__name__)


def get_root(misc: Misc) -> Tk:
    return misc.nametowidget(".")


@overload
def scaling(master: Misc, factor: None = None) -> float: ...
@overload
def scaling(master: Misc, factor: float) -> None: ...
def scaling(master: Misc, factor: float | None = None) -> float | None:
    """设置或获取 GUI 缩放比例因子

    当传入 factor 参数时，设置当前缩放比例并应用新的缩放因子到 Tkinter 窗口。
    不传入参数时返回当前缩放比例因子。

    与 tk scaling ?-displayof window? ?number? 相同。

    - Tk 手册页：https://www.tcl-lang.org/man/tcl8.6/TkCmd/tk.htm
    """
    root = get_root(master)
    if factor is not None:
        master.tk.call("tk", "scaling", factor)
        setattr(root, ATTR_SCALING_CACHED, factor)
        return None
    if hasattr(root, ATTR_SCALING_CACHED):
        return getattr(root, ATTR_SCALING_CACHED)

    factor = master.tk.call("tk", "scaling")
    setattr(root, ATTR_SCALING_CACHED, factor)
    return factor


@overload
def scale(master: Misc, value: int) -> int: ...
@overload
def scale(master: Misc, value: float) -> float: ...


def scale(master: Misc, value: float) -> int | float:
    if isinstance(value, int):
        return int(scaling(master) * value)
    return float(scaling(master) * value)


@overload
def scale_args(master: Misc, *args: int) -> tuple[int, ...]: ...
@overload
def scale_args(master: Misc, *args: float) -> tuple[float, ...]: ...
def scale_args(master: Misc, *args: float) -> tuple[Any, ...]:
    return tuple(scale(master, value) for value in args)


def scale_kw(master: Misc, **kwargs: float) -> dict[str, Any]:
    return {key: scale(master, value) for key, value in kwargs.items()}
