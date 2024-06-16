from tkinter import Label, Event

from tkinter.ttk import Label as TtkLabel
from typing import Callable, Union

from vcf_generator.ui.base import BaseWindow


def get_auto_wrap_event(label: Union[Label, TtkLabel], min_width: int = 0) -> Callable[[Event], None]:
    """
    返回一个用于自动调整标签（Label 或T tkLabel）换行长度的事件处理函数。

    :param window: 基础窗口类实例，用于获取缩放比例
    :param label: 要自动换行的 Tkinter 或 Ttk Label 实例
    :param min_width: 标签最小宽度（虚拟像素），默认为 0
    :return: 事件处理函数，接受一个事件参数并根据组件大小和给定的最小宽度调整标签的wraplength属性
    """
    window = label.master
    real_min_width = window.get_scaled(min_width) if isinstance(window, BaseWindow) else min_width
    return lambda event: label.configure(wraplength=max(event.width, real_min_width))
