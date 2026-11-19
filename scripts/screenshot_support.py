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
    import tkinter.font
    from tkinter import Misc

    from PIL import Image

# 持有重建的命名字体，避免 Font 析构时删除字体导致符号回退到默认字体。
_SYMBOL_FONTS: dict[int, list[tkinter.font.Font]] = {}

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
            # 9pt 与 Windows 参考截图的系统字体字号一致。
            tkinter.font.nametofont(name, root=root).configure(family=family, size=9)
        except tkinter.TclError:
            continue


def unify_warning_symbol_font(widget: Misc, family: str) -> None:
    """把 widget 内所有 U+26A0 警告符号的字体族统一为 family。

    截图脚本按语言设置不同 Tk 字体族：zh-CN 用 Noto Sans CJK SC（自带该符号，粗描边圆角），
    en-US 用 Noto Sans（不含该符号，回退到 DejaVu Sans，细描边空心），导致同一符号两语种渲染不一致。
    仅把 family 设成 en-US 的 Noto Sans 还不够：zh_CN locale 下 fontconfig 会优先回退到同样含该字形的
    Noto Sans CJK SC（粗描边圆角），而非 DejaVu Sans。因此按符号字符本身定位 Label，直接锁定 family
    为含该字形且细描边空心的 DejaVu Sans，两语种都命中同一字体，贴近 Windows 参考图且不改运行时代码。
    """
    import tkinter.font

    symbol = "\u26a0"
    labels: list[Misc] = []

    def walk(node: Misc) -> None:
        for child in node.winfo_children():
            try:
                is_symbol = str(child.cget("text")) == symbol
            except tkinter.TclError:
                is_symbol = False
            if is_symbol:
                labels.append(child)
            walk(child)

    walk(widget)
    if not labels:
        raise SystemExit(f"未找到文本为 {symbol!r} 的 Label，无法统一警告符号字体。")

    # 原 Label 字体是匿名 Font，其 Python 对象析构后命名字体会从 font names 中消失；
    # Font(font=...) 内部走 font actual 仍能读到其完整配置，据此复制并仅替换 family，保留原 size。
    # 用模块级表持有新字体，防止 Font 析构删除命名字体导致符号回退到默认字体。
    fonts: list[tkinter.font.Font] = []
    for label in labels:
        font = tkinter.font.Font(font=label.cget("font"))
        font.configure(family=family)
        label["font"] = font
        fonts.append(font)
    _SYMBOL_FONTS[id(widget)] = fonts


def grab_window(window: Misc, platform: str) -> Image.Image:
    """抓取窗口（含装饰、不含阴影）；Linux 为不透明矩形，macOS 自带透明圆角。"""
    if platform == "macos":
        return _grab_macos(window)
    return _grab_linux(window)


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


def _grab_macos(window: Misc) -> Image.Image:
    from PIL import Image

    # -o 去除窗口阴影；窗口截图自带圆角外的透明像素。
    screencapture = require_executable("screencapture")
    window_id = _window_id_macos(window)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as target:
        target_path = Path(target.name)
    try:
        subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true]
            [screencapture, "-o", "-x", "-l", str(window_id), str(target_path)],
            check=True,
        )
        with Image.open(target_path) as image:
            return image.convert("RGBA")
    finally:
        target_path.unlink(missing_ok=True)


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


def _grab_linux(window: Misc) -> Image.Image:
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
        # 抓 root 窗口上 frame 所占区域：形状外（圆角）像素才能带上根背景色，
        # 亮/暗两版由此产生差异并反推 alpha；抓 frame 自身缓冲则形状外恒为黑。
        image_ptr = x11.XGetImage(display, root, x, y, width, height, ALL_PLANES, ZPIXMAP)
        if not image_ptr:
            raise SystemExit("XGetImage 失败。")
        try:
            image = image_ptr.contents
            if image.bits_per_pixel != 32:
                raise SystemExit(f"不支持的像素深度：{image.bits_per_pixel} bpp。")
            buffer = ctypes.string_at(image.data, image.bytes_per_line * image.height)
            result = Image.frombuffer(
                "RGBA", (image.width, image.height), buffer, "raw", "BGRA", image.bytes_per_line, 1
            )
            result.putalpha(255)
            return result
        finally:
            x11.XDestroyImage(image_ptr)
    finally:
        x11.XCloseDisplay(display)


def derive_transparent(light: Image.Image, dark: Image.Image) -> Image.Image:
    """由亮/暗背景两版抓取反推逐像素 alpha 与前景色。

    亮底 L = F*a + 255*(1-a)，暗底 D = F*a，故 a = 255 - (L - D)。
    """
    from PIL import Image

    if light.size != dark.size:
        raise SystemExit("亮暗两版尺寸不一致，无法反推透明。")
    light_rgb = light.convert("RGB")
    dark_rgb = dark.convert("RGB")
    lb = light_rgb.tobytes()
    db = dark_rgb.tobytes()
    out = bytearray(len(lb) // 3 * 4)
    for i in range(0, len(lb), 3):
        alpha = 255 - (lb[i] - db[i])
        alpha = max(0, min(255, alpha))
        j = i // 3 * 4
        if alpha:
            out[j] = db[i] * 255 // alpha
            out[j + 1] = db[i + 1] * 255 // alpha
            out[j + 2] = db[i + 2] * 255 // alpha
        out[j + 3] = alpha
    return Image.frombytes("RGBA", light_rgb.size, bytes(out))


def composite_over(image: Image.Image, color: str) -> Image.Image:
    from PIL import Image

    background = Image.new("RGBA", image.size, color)
    return Image.alpha_composite(background, image.convert("RGBA")).convert("RGB")


def save_image(image: Image.Image, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="png")
    image.save(output.with_suffix(".webp"), format="WEBP", quality=100, method=6, lossless=True)
    print(f"已保存：{output}", flush=True)
