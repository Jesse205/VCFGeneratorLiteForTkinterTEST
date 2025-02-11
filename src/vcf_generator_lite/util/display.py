"""
高DPI显示缩放处理模块 (跨平台支持)

本模块提供系统级DPI缩放检测和适配功能，主要解决高分辨率屏幕下Tkinter界面模糊问题。

"""
import sys
from tkinter import Misc

if sys.platform == "win32":
    from .display_windows import enable_dpi_aware_windows, get_scale_factor_windows

__all__ = ["enable_dpi_aware", "get_scale_factor"]


def enable_dpi_aware():
    """
    启用 DPI 自动感知

    针对 Windows 平台：
    - 禁用 DPI 虚拟化 (DPI virtualization)，消除界面模糊现象
    - 调用 Windows win32 API 设置进程级 DPI 感知策略

    非 Windows 平台：
    - 当前保持空实现，后续可按需扩展其他系统支持
    """

    try:
        if sys.platform == "win32":
            enable_dpi_aware_windows()
    except RuntimeError as e:
        print("Failed to get scale factor", e, file=sys.stderr)


def get_scale_factor(misc: Misc) -> float:
    """
    获取缩放因子。

    在不同操作系统上获取缩放因子，以便在高 DPI 屏幕上正确显示界面。
    缩放因子影响如何将逻辑坐标转换为屏幕坐标。

    :param misc: Tkinter 根对象(Tk 或 Toplevel)，用于跨平台兼容性参数传递，实际实现可能根据平台不同忽略此参数
    :return: 系统缩放系数(例如 1.5 表示 150% 缩放)，无法检测时默认返回 1.0
    """

    try:
        if sys.platform == "win32":
            return get_scale_factor_windows(misc)
    except Exception as e:
        print("Failed to get scale factor", e, file=sys.stderr)
    return 1.0
