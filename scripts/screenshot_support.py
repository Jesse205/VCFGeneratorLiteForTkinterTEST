"""截图流程的跨平台支撑函数（Linux / macOS）。"""

from __future__ import annotations

import ctypes
import ctypes.util
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tkinter import Misc


FONT_NAMES = (
    "TkDefaultFont",
    "TkTextFont",
    "TkFixedFont",
    "TkMenuFont",
    "TkHeadingFont",
    "TkCaptionFont",
    "TkSmallCaptionFont",
    "TkIconFont",
    "TkTooltipFont",
)

SWIFT_WINDOW_ID = """
import CoreGraphics
import Foundation

let pid = Int32(CommandLine.arguments[1])!
let targetWidth = Double(CommandLine.arguments[2])!
let options: CGWindowListOption = [.optionOnScreenOnly, .excludeDesktopElements]
let windows = CGWindowListCopyWindowInfo(options, kCGNullWindowID) as? [[String: Any]] ?? []
for window in windows {
    guard let owner = window[kCGWindowOwnerPID as String] as? Int, owner == Int(pid) else { continue }
    guard let layer = window[kCGWindowLayer as String] as? Int, layer == 0 else { continue }
    guard let boundsDict = window[kCGWindowBounds as String] as? NSDictionary,
          let bounds = CGRect(dictionaryRepresentation: boundsDict as CFDictionary) else { continue }
    if abs(bounds.width - targetWidth) <= 16, let number = window[kCGWindowNumber as String] as? Int {
        print(number)
        exit(0)
    }
}
exit(1)
"""

ZPIXMAP = 2
ALL_PLANES = 0xFFFFFFFF


class XImage(ctypes.Structure):
    """libX11 ``XImage`` 的前导字段，仅用于读取像素缓冲。"""

    _fields_ = [
        ("width", ctypes.c_int),
        ("height", ctypes.c_int),
        ("xoffset", ctypes.c_int),
        ("format", ctypes.c_int),
        ("data", ctypes.c_void_p),
        ("byte_order", ctypes.c_int),
        ("bitmap_unit", ctypes.c_int),
        ("bitmap_bit_order", ctypes.c_int),
        ("bitmap_pad", ctypes.c_int),
        ("depth", ctypes.c_int),
        ("bytes_per_line", ctypes.c_int),
        ("bits_per_pixel", ctypes.c_int),
        ("red_mask", ctypes.c_ulong),
        ("green_mask", ctypes.c_ulong),
        ("blue_mask", ctypes.c_ulong),
    ]


def require_executable(name: str) -> str:
    path = shutil.which(name)
    if path is None:
        raise SystemExit(f"未找到可执行文件：{name}")
    return path


def apply_tk_fonts(root: Misc, family: str) -> None:
    """在创建控件前统一替换 Tk 内置命名字体。"""
    import tkinter.font

    families = set(tkinter.font.families(root))
    if family not in families:
        sample = ", ".join(sorted(families)[:20])
        raise SystemExit(f"找不到字体 {family!r}。当前可用字体示例：{sample}")

    for name in FONT_NAMES:
        try:
            tkinter.font.nametofont(name, root=root).configure(family=family)
        except tkinter.TclError:
            continue


def pump(window: Misc, seconds: float) -> None:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        window.update()
        time.sleep(0.03)


def capture_window(window: Misc, output: Path, platform: str) -> Path:
    """截取窗口（含装饰、不含阴影），输出带 alpha 通道的 PNG。"""
    output.parent.mkdir(parents=True, exist_ok=True)
    if platform == "macos":
        _capture_macos(window, output)
    else:
        _capture_linux(window, output)
    return output


def _window_id_macos(window: Misc) -> int:
    swift = require_executable("swift")
    width = window.winfo_width()
    with tempfile.NamedTemporaryFile("w", suffix=".swift", delete=False, encoding="utf-8") as source:
        source.write(SWIFT_WINDOW_ID)
        source_path = Path(source.name)
    try:
        result = subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true]
            [swift, str(source_path), str(os.getpid()), str(width)],
            check=True,
            capture_output=True,
            text=True,
        )
    finally:
        source_path.unlink(missing_ok=True)
    return int(result.stdout.strip().splitlines()[0])


def _capture_macos(window: Misc, output: Path) -> None:
    # -o 去除窗口阴影；窗口截图自带圆角外的透明像素。
    screencapture = require_executable("screencapture")
    window_id = _window_id_macos(window)
    subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true]
        [screencapture, "-o", "-x", "-l", str(window_id), str(output)],
        check=True,
    )


def _open_x11() -> tuple[ctypes.CDLL, ctypes.c_void_p]:
    library = ctypes.util.find_library("X11")
    if library is None:
        raise SystemExit("未找到 libX11。")
    x11 = ctypes.CDLL(library)
    x11.XOpenDisplay.argtypes = [ctypes.c_char_p]
    x11.XOpenDisplay.restype = ctypes.c_void_p
    x11.XCloseDisplay.argtypes = [ctypes.c_void_p]
    display = x11.XOpenDisplay(None)
    if not display:
        raise SystemExit("无法连接 X11 显示。")
    return x11, display


def _linux_frame_id(x11: ctypes.CDLL, display: ctypes.c_void_p, window: Misc) -> int:
    x11.XQueryTree.argtypes = [
        ctypes.c_void_p,
        ctypes.c_ulong,
        ctypes.POINTER(ctypes.c_ulong),
        ctypes.POINTER(ctypes.c_ulong),
        ctypes.POINTER(ctypes.POINTER(ctypes.c_ulong)),
        ctypes.POINTER(ctypes.c_uint),
    ]
    x11.XQueryTree.restype = ctypes.c_int
    x11.XFree.argtypes = [ctypes.c_void_p]

    original = window.winfo_id()
    xid = original
    for _ in range(50):
        root = ctypes.c_ulong()
        parent = ctypes.c_ulong()
        children = ctypes.POINTER(ctypes.c_ulong)()
        count = ctypes.c_uint()
        if not x11.XQueryTree(
            display, xid, ctypes.byref(root), ctypes.byref(parent), ctypes.byref(children), ctypes.byref(count)
        ):
            raise SystemExit("XQueryTree 失败。")
        if children:
            x11.XFree(children)
        if parent.value == root.value:
            if xid == original:
                time.sleep(0.05)
                continue
            return xid
        xid = parent.value
    raise SystemExit("未找到窗口管理器装饰，请先启动 xfwm4 等窗口管理器。")


def _capture_linux(window: Misc, output: Path) -> None:
    from PIL import Image

    x11, display = _open_x11()
    try:
        frame = _linux_frame_id(x11, display, window)
        x11.XGetGeometry.argtypes = [
            ctypes.c_void_p,
            ctypes.c_ulong,
            ctypes.POINTER(ctypes.c_ulong),
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_uint),
            ctypes.POINTER(ctypes.c_uint),
            ctypes.POINTER(ctypes.c_uint),
            ctypes.POINTER(ctypes.c_uint),
        ]
        x11.XGetGeometry.restype = ctypes.c_int
        root = ctypes.c_ulong()
        x = ctypes.c_int()
        y = ctypes.c_int()
        width = ctypes.c_uint()
        height = ctypes.c_uint()
        border = ctypes.c_uint()
        depth = ctypes.c_uint()
        if not x11.XGetGeometry(
            display,
            frame,
            ctypes.byref(root),
            ctypes.byref(x),
            ctypes.byref(y),
            ctypes.byref(width),
            ctypes.byref(height),
            ctypes.byref(border),
            ctypes.byref(depth),
        ):
            raise SystemExit("XGetGeometry 失败。")
        x11.XGetImage.argtypes = [
            ctypes.c_void_p,
            ctypes.c_ulong,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_ulong,
            ctypes.c_int,
        ]
        x11.XGetImage.restype = ctypes.POINTER(XImage)
        x11.XDestroyImage.argtypes = [ctypes.POINTER(XImage)]
        x11.XDestroyImage.restype = ctypes.c_int
        image_ptr = x11.XGetImage(display, frame, 0, 0, width, height, ALL_PLANES, ZPIXMAP)
        if not image_ptr:
            raise SystemExit("XGetImage 失败。")
        try:
            image = image_ptr.contents
            if image.bits_per_pixel != 32:
                raise SystemExit(f"不支持的像素深度：{image.bits_per_pixel} bpp。")
            buffer = ctypes.string_at(image.data, image.bytes_per_line * image.height)
            # 装饰为直角矩形，X11 无逐像素 alpha；统一补不透明 alpha 通道。
            result = Image.frombuffer(
                "RGBA", (image.width, image.height), buffer, "raw", "BGRA", image.bytes_per_line, 1
            )
            result.putalpha(255)
            result.save(output, format="png")
        finally:
            x11.XDestroyImage(image_ptr)
    finally:
        x11.XCloseDisplay(display)


def save_capture_as_webp(source: Path, output: Path) -> None:
    from PIL import Image

    output.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        image.convert("RGBA").save(output, format="WEBP", quality=100, method=6, lossless=True)
