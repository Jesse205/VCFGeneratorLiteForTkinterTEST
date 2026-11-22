"""截图流程的跨平台支撑函数（Linux / macOS）。"""

from __future__ import annotations

import ctypes
import ctypes.util
import os
import platform
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import TYPE_CHECKING

from PIL import Image

if TYPE_CHECKING:
    from tkinter import Misc

SWIFT_GRAB_WINDOW = """
import CoreGraphics
import Foundation
import ImageIO

let pid = Int32(CommandLine.arguments[1])!
let targetWidth = Double(CommandLine.arguments[2])!
let outputPath = CommandLine.arguments[3]
let windows = CGWindowListCopyWindowInfo([.optionOnScreenOnly, .excludeDesktopElements], kCGNullWindowID)
    as? [[String: Any]] ?? []
// 始终 dump 窗口列表到 stderr，便于在 CI 日志中核查匹配过程。
for window in windows {
    let number = window[kCGWindowNumber as String] ?? "?"
    let owner = window[kCGWindowOwnerPID as String] ?? "?"
    let layer = window[kCGWindowLayer as String] ?? "?"
    let bounds = window[kCGWindowBounds as String] ?? "?"
    fputs("window number=\\(number) pid=\\(owner) layer=\\(layer) bounds=\\(bounds)\\n", stderr)
}
fputs("target pid=\\(pid) width=\\(targetWidth)\\n", stderr)
var matched: CGWindowID?
for window in windows {
    guard let owner = window[kCGWindowOwnerPID as String] as? Int, owner == Int(pid) else { continue }
    // Tk 8.6 在 macOS 上的窗口 CG layer 为 19（utility 层），不能用 layer == 0 过滤；
    // 仅排除菜单栏(24)/状态栏(25)等系统层，靠 pid + 宽度匹配锁定目标窗口。
    guard let layer = window[kCGWindowLayer as String] as? Int, layer < 24 else { continue }
    guard let boundsDict = window[kCGWindowBounds as String] as? NSDictionary,
          let bounds = CGRect(dictionaryRepresentation: boundsDict as CFDictionary) else { continue }
    if abs(bounds.width - targetWidth) <= 16, let number = window[kCGWindowNumber as String] {
        matched = CGWindowID(number as! Int)
        break
    }
}
guard let windowID = matched else {
    fputs("no window matched pid=\\(pid) width=\\(targetWidth)\\n", stderr)
    exit(1)
}
// 直接抓窗口位图：抓取自身进程的窗口无需屏幕录制 TCC 权限（screencapture 子进程无权限时
// 会降级为屏幕区域截屏，弹窗场景会混入背后主窗内容）。optionIncludingWindow 只取单窗，
// boundsIgnoreFraming 去阴影留白，图像自带圆角外透明像素。API 虽自 10.11 标记废弃，仍可用。
guard let image = CGWindowListCreateImage(
    .null, .optionIncludingWindow, windowID, [.boundsIgnoreFraming, .bestResolution]
) else {
    fputs("CGWindowListCreateImage returned nil for window \\(windowID)\\n", stderr)
    exit(2)
}
let url = URL(fileURLWithPath: outputPath) as CFURL
guard let destination = CGImageDestinationCreateWithURL(url, "public.png" as CFString, 1, nil) else {
    fputs("failed to create image destination for \\(outputPath)\\n", stderr)
    exit(3)
}
CGImageDestinationAddImage(destination, image, nil)
guard CGImageDestinationFinalize(destination) else {
    fputs("failed to finalize PNG at \\(outputPath)\\n", stderr)
    exit(3)
}
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


def grab_window(window: Misc, platform: str) -> Image.Image:
    """抓取窗口（含装饰、不含阴影）；Linux 为不透明矩形，macOS 自带透明圆角，Windows 走 PrintWindow。"""
    if platform == "macos":
        return _grab_macos(window)
    if platform == "windows":
        from scripts.screenshot_windows import grab_window_windows

        return grab_window_windows(window)
    return _grab_linux(window)


def _grab_macos(window: Misc) -> Image.Image:
    """用 Swift 调 CGWindowListCreateImage 抓当前窗口位图（含装饰、去阴影、圆角外透明）。"""
    from PIL import Image

    swift = require_executable("swift")
    width = window.winfo_width()
    with tempfile.NamedTemporaryFile("w", suffix=".swift", delete=False, encoding="utf-8") as source:
        source.write(SWIFT_GRAB_WINDOW)
        source_path = Path(source.name)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as target:
        target_path = Path(target.name)
    try:
        # CGWindowListCreateImage 在 macOS 15 SDK 标记 obsoleted；把 deployment target 降到 14
        # 使其降级为警告（runner 为 Intel，机器架构动态获取）。运行时系统仍保留该 shim。
        target_triple = f"{platform.machine()}-apple-macos14.0"
        subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true]
            [swift, "-target", target_triple, str(source_path), str(os.getpid()), str(width), str(target_path)],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as error:
        raise SystemExit(
            f"Swift 抓窗失败（pid={os.getpid()}，width={width}）：\n{error.stderr}"
        ) from error
    finally:
        source_path.unlink(missing_ok=True)
    try:
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

    混合模型 C = F*a + bg*(1-a)：三通道各自隐含 alpha = 1-(L-D)/255，取最大者
    （即最保守的 alpha），前景 F = (D-bg)/a + bg（暗底 bg=0 即 F=D/a），
    alpha 近 0 处保留原色。算法与 lab/transparent-window-img 的 core.process 一致。
    """
    light_rgb = light.convert("RGB")
    dark_rgb = dark.convert("RGB")
    lb = light_rgb.tobytes()
    db = dark_rgb.tobytes()
    out = bytearray(len(lb) // 3 * 4)
    for i in range(0, len(lb), 3):
        max_gap = max(lb[i] - db[i], lb[i + 1] - db[i + 1], lb[i + 2] - db[i + 2])
        alpha = (255 - max_gap) / 255
        j = i // 3 * 4
        if alpha > 0.001:
            for k in range(3):
                out[j + k] = min(255, max(0, round(db[i + k] / alpha)))
            out[j + 3] = min(255, round(alpha * 255))
        else:
            out[j] = db[i]
            out[j + 1] = db[i + 1]
            out[j + 2] = db[i + 2]
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
