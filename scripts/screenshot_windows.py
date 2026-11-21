"""截图支撑：字体临时注册、系统级字体/DPI 覆盖（均带备份还原）、PrintWindow 抓图。

字体注册在 Windows 为会话级（AddFontResourceW）、macOS/Linux 为用户级（复制到用户字体目录），
二者都不是进程级，故统一用上下文管理器在退出时还原。所有 ctypes.WinDLL 调用懒加载，
避免在 Linux/macOS 导入时失败。
"""

from __future__ import annotations

import ctypes
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from tkinter import Misc

    from PIL import Image

SPIF_UPDATEINIFILE = 0x01
SPI_GETNONCLIENTMETRICS = 0x0029
SPI_SETNONCLIENTMETRICS = 0x002A
SPI_GETICONTITLELOGFONT = 0x001F
SPI_SETICONTITLELOGFONT = 0x0022
HWND_BROADCAST = 0xFFFF
WM_SETTINGCHANGE = 0x001A
WM_FONTCHANGE = 0x001D
SMTO_ABORTIFHUNG = 0x0002
WINDOW_METRICS = "WindowMetrics"
DWMWA_EXTENDED_FRAME_BOUNDS = 9
GA_ROOT = 2

QDC_ONLY_ACTIVE_PATHS = 2
GET_DPI_SCALE = 0xFFFFFFFD
SET_DPI_SCALE = 0xFFFFFFFC

DPI_PERCENTS = (100, 125, 150, 175, 200, 225, 250, 300, 350, 400, 450, 500)


class LOGFONTW(ctypes.Structure):
    _fields_ = [
        ("lfHeight", ctypes.c_long),
        ("lfWidth", ctypes.c_long),
        ("lfEscapement", ctypes.c_long),
        ("lfOrientation", ctypes.c_long),
        ("lfWeight", ctypes.c_long),
        ("lfItalic", ctypes.c_byte),
        ("lfUnderline", ctypes.c_byte),
        ("lfStrikeOut", ctypes.c_byte),
        ("lfCharSet", ctypes.c_byte),
        ("lfOutPrecision", ctypes.c_byte),
        ("lfClipPrecision", ctypes.c_byte),
        ("lfQuality", ctypes.c_byte),
        ("lfPitchAndFamily", ctypes.c_byte),
        ("lfFaceName", ctypes.c_wchar * 32),
    ]


class NONCLIENTMETRICSW(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_uint),
        ("iBorderWidth", ctypes.c_int),
        ("iScrollWidth", ctypes.c_int),
        ("iScrollHeight", ctypes.c_int),
        ("iCaptionWidth", ctypes.c_int),
        ("iCaptionHeight", ctypes.c_int),
        ("lfCaptionFont", LOGFONTW),
        ("iSmCaptionWidth", ctypes.c_int),
        ("iSmCaptionHeight", ctypes.c_int),
        ("lfSmCaptionFont", LOGFONTW),
        ("iMenuWidth", ctypes.c_int),
        ("iMenuHeight", ctypes.c_int),
        ("lfMenuFont", LOGFONTW),
        ("lfStatusFont", LOGFONTW),
        ("lfMessageFont", LOGFONTW),
        ("iPaddedBorderWidth", ctypes.c_int),
    ]


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", ctypes.c_ulong),
        ("biWidth", ctypes.c_long),
        ("biHeight", ctypes.c_long),
        ("biPlanes", ctypes.c_ushort),
        ("biBitCount", ctypes.c_ushort),
        ("biCompression", ctypes.c_ulong),
        ("biSizeImage", ctypes.c_ulong),
        ("biXPelsPerMeter", ctypes.c_long),
        ("biYPelsPerMeter", ctypes.c_long),
        ("biClrUsed", ctypes.c_ulong),
        ("biClrImportant", ctypes.c_ulong),
    ]


class BITMAPINFO(ctypes.Structure):
    _fields_ = [("bmiHeader", BITMAPINFOHEADER), ("bmiColors", ctypes.c_ulong * 3)]


class LUID(ctypes.Structure):
    _fields_ = [("LowPart", ctypes.c_ulong), ("HighPart", ctypes.c_long)]


class PathSourceInfo(ctypes.Structure):
    _fields_ = [
        ("adapterId", LUID),
        ("id", ctypes.c_uint),
        ("modeInfoIdx", ctypes.c_uint),
        ("statusFlags", ctypes.c_uint),
    ]


class RATIONAL(ctypes.Structure):
    _fields_ = [("Numerator", ctypes.c_uint), ("Denominator", ctypes.c_uint)]


class PathTargetInfo(ctypes.Structure):
    _fields_ = [
        ("adapterId", LUID),
        ("id", ctypes.c_uint),
        ("modeInfoIdx", ctypes.c_uint),
        ("outputTechnology", ctypes.c_uint),
        ("rotation", ctypes.c_uint),
        ("scaling", ctypes.c_uint),
        ("refreshRate", RATIONAL),
        ("scanLineOrdering", ctypes.c_uint),
        ("targetAvailable", ctypes.c_int),
        ("statusFlags", ctypes.c_uint),
    ]


class PathInfo(ctypes.Structure):
    _fields_ = [
        ("sourceInfo", PathSourceInfo),
        ("targetInfo", PathTargetInfo),
        ("flags", ctypes.c_uint),
    ]


class DeviceInfoHeader(ctypes.Structure):
    _fields_ = [("type", ctypes.c_uint), ("size", ctypes.c_uint), ("adapterId", LUID), ("id", ctypes.c_uint)]


class DpiScale(ctypes.Structure):
    _fields_ = [
        ("header", DeviceInfoHeader),
        ("minScaleRel", ctypes.c_long),
        ("curScaleRel", ctypes.c_long),
        ("maxScaleRel", ctypes.c_long),
    ]


class DpiScaleSet(ctypes.Structure):
    _fields_ = [("header", DeviceInfoHeader), ("scaleRel", ctypes.c_uint)]


class FontsInstalled:
    """临时注册字体（Windows 会话级 / Unix 用户级），退出时按备份还原。

    - Windows: AddFontResourceW 注册到当前会话，退出时 RemoveFontResourceW 撤销。
    - macOS/Linux: 复制字体到用户目录，退出时仅删除本次新增文件、恢复被覆盖的同名文件，
      并重建 fontconfig 缓存。字体若已在环境中存在则无需注册（空操作）。
    """

    def __init__(self, font_dir: Path):
        self.font_dir = font_dir
        self.font_files = sorted((*font_dir.glob("*.ttf"), *font_dir.glob("*.otf")))
        if not self.font_files:
            raise SystemExit(f"字体目录中没有 .ttf/.otf 文件：{font_dir}")
        self.user_font_dir = (
            Path.home() / "Library" / "Fonts"
            if sys.platform == "darwin"
            else Path.home() / ".local" / "share" / "fonts"
        )
        # 记录被覆盖的原文件（目标路径 -> 原字节），退出时据此还原；None 表示原本不存在。
        self._backups: dict[Path, bytes | None] = {}
        self._installed = False

    def __enter__(self) -> Self:
        """注册字体并记录备份。"""
        if sys.platform == "win32":
            gdi32 = ctypes.WinDLL("gdi32")
            user32 = ctypes.WinDLL("user32")
            gdi32.AddFontResourceW.argtypes = [ctypes.c_wchar_p]
            gdi32.AddFontResourceW.restype = ctypes.c_int
            gdi32.RemoveFontResourceW.argtypes = [ctypes.c_wchar_p]
            gdi32.RemoveFontResourceW.restype = ctypes.c_int
            for font_file in self.font_files:
                gdi32.AddFontResourceW(str(font_file.resolve()))
            _broadcast_message(user32, WM_FONTCHANGE, 0, None)
            self._installed = True
            return self

        self.user_font_dir.mkdir(parents=True, exist_ok=True)
        for font_file in self.font_files:
            target = self.user_font_dir / font_file.name
            self._backups[target] = target.read_bytes() if target.exists() else None
            shutil.copy2(font_file, target)
        self._refresh_font_cache()
        self._installed = True
        return self

    def __exit__(self, *_exc: object) -> None:
        """撤销字体注册，按备份还原用户字体目录。"""
        if not self._installed:
            return
        if sys.platform == "win32":
            gdi32 = ctypes.WinDLL("gdi32")
            user32 = ctypes.WinDLL("user32")
            gdi32.RemoveFontResourceW.argtypes = [ctypes.c_wchar_p]
            gdi32.RemoveFontResourceW.restype = ctypes.c_int
            for font_file in self.font_files:
                gdi32.RemoveFontResourceW(str(font_file.resolve()))
            _broadcast_message(user32, WM_FONTCHANGE, 0, None)
            return
        for target, original in self._backups.items():
            if original is None:
                target.unlink(missing_ok=True)
            else:
                target.write_bytes(original)
        self._refresh_font_cache()

    def _refresh_font_cache(self) -> None:
        if sys.platform.startswith("linux") and (fc_cache := shutil.which("fc-cache")) is not None:
            subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true]
                [fc_cache, "-f", str(self.user_font_dir)],
                check=False,
            )


def _broadcast_message(user32: ctypes.WinDLL, message: int, wparam: int, lparam_text: str | None) -> None:
    result = ctypes.c_size_t()
    lparam = ctypes.cast(ctypes.c_wchar_p(lparam_text), ctypes.c_void_p).value if lparam_text else 0
    user32.SendMessageTimeoutW.argtypes = [
        ctypes.c_void_p,
        ctypes.c_uint,
        ctypes.c_size_t,
        ctypes.c_ssize_t,
        ctypes.c_uint,
        ctypes.c_uint,
        ctypes.POINTER(ctypes.c_size_t),
    ]
    user32.SendMessageTimeoutW(
        HWND_BROADCAST,
        message,
        wparam,
        lparam,
        SMTO_ABORTIFHUNG,
        1000,
        ctypes.byref(result),
    )


class WindowsSystemSettings:
    """按 noMeiryoUI 的逻辑临时修改系统字体，并切换到目标缩放，退出时还原。"""

    def __init__(self, family: str, scale: float, size_pt: float = 9.0):
        self.family = family
        self.scale = scale
        self.size_pt = size_pt
        self._user32 = ctypes.WinDLL("user32")
        self._user32.SystemParametersInfoW.argtypes = [ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p, ctypes.c_uint]
        self._user32.SystemParametersInfoW.restype = ctypes.c_int
        self._user32.GetDpiForSystem.restype = ctypes.c_uint
        self._user32.GetDisplayConfigBufferSizes.argtypes = [
            ctypes.c_uint,
            ctypes.POINTER(ctypes.c_uint),
            ctypes.POINTER(ctypes.c_uint),
        ]
        self._user32.QueryDisplayConfig.argtypes = [
            ctypes.c_uint,
            ctypes.POINTER(ctypes.c_uint),
            ctypes.POINTER(PathInfo),
            ctypes.POINTER(ctypes.c_uint),
            ctypes.c_void_p,
            ctypes.c_void_p,
        ]
        self._user32.DisplayConfigGetDeviceInfo.argtypes = [ctypes.c_void_p]
        self._user32.DisplayConfigSetDeviceInfo.argtypes = [ctypes.c_void_p]
        self._source_adapter, self._source_id = self._query_display_source()
        self._saved_relative: int | None = None
        self._min_relative = 0
        self._max_relative = 0
        self._saved_ncm: NONCLIENTMETRICSW | None = None
        self._saved_icon: LOGFONTW | None = None

    def __enter__(self) -> Self:
        """保存当前 DPI 与字体，然后应用目标缩放和字体。"""
        scale = self._get_scale()
        self._saved_relative = scale.curScaleRel
        self._min_relative = scale.minScaleRel
        self._max_relative = scale.maxScaleRel
        self._saved_ncm = self._get_ncm()
        self._saved_icon = self._get_icon_font()
        self._apply_dpi_scale()
        self._apply_font()
        return self

    def __exit__(self, *_exc: object) -> None:
        """还原进入时保存的 DPI 与字体。"""
        if self._saved_relative is not None:
            self._set_scale(self._saved_relative)
        if self._saved_ncm is not None:
            self._set_ncm(self._saved_ncm)
        if self._saved_icon is not None:
            self._set_icon_font(self._saved_icon)

    def _get_dpi(self) -> int:
        if hasattr(self._user32, "GetDpiForSystem"):
            return int(self._user32.GetDpiForSystem())
        gdi32 = ctypes.WinDLL("gdi32")
        hdc = self._user32.GetDC(0)
        try:
            return int(gdi32.GetDeviceCaps(hdc, 90))
        finally:
            self._user32.ReleaseDC(0, hdc)

    def _query_display_source(self) -> tuple[LUID, int]:
        path_count = ctypes.c_uint(0)
        mode_count = ctypes.c_uint(0)
        rc = self._user32.GetDisplayConfigBufferSizes(
            QDC_ONLY_ACTIVE_PATHS, ctypes.byref(path_count), ctypes.byref(mode_count)
        )
        if rc != 0:
            raise SystemExit(f"读取显示配置失败：{rc}")
        paths = (PathInfo * path_count.value)()
        modes = ctypes.create_string_buffer(mode_count.value * 64)
        rc = self._user32.QueryDisplayConfig(
            QDC_ONLY_ACTIVE_PATHS,
            ctypes.byref(path_count),
            paths,
            ctypes.byref(mode_count),
            ctypes.cast(modes, ctypes.c_void_p),
            None,
        )
        if rc != 0:
            raise SystemExit(f"查询显示路径失败：{rc}")
        for index in range(path_count.value):
            path = paths[index]
            if path.targetInfo.targetAvailable:
                return path.sourceInfo.adapterId, path.sourceInfo.id
        raise SystemExit("未找到可用的显示路径。")

    def _get_scale(self) -> DpiScale:
        packet = DpiScale()
        packet.header.type = GET_DPI_SCALE
        packet.header.size = ctypes.sizeof(packet)
        packet.header.adapterId = self._source_adapter
        packet.header.id = self._source_id
        rc = self._user32.DisplayConfigGetDeviceInfo(ctypes.byref(packet))
        if rc != 0:
            raise SystemExit(f"读取 DPI 缩放失败：{rc}")
        return packet

    def _set_scale(self, relative: int) -> None:
        packet = DpiScaleSet()
        packet.header.type = SET_DPI_SCALE
        packet.header.size = ctypes.sizeof(packet)
        packet.header.adapterId = self._source_adapter
        packet.header.id = self._source_id
        packet.scaleRel = relative & 0xFFFFFFFF
        rc = self._user32.DisplayConfigSetDeviceInfo(ctypes.byref(packet))
        if rc != 0:
            raise SystemExit(f"设置 DPI 缩放失败：{rc}")
        time.sleep(0.3)

    def _apply_dpi_scale(self) -> None:
        if self._saved_relative is None:
            return
        current_dpi = self._get_dpi()
        current_percent = min(DPI_PERCENTS, key=lambda percent: abs(percent - current_dpi * 100 / 96))
        current_index = DPI_PERCENTS.index(current_percent)
        recommended_index = current_index - self._saved_relative
        target_percent = round(self.scale * 100)
        if target_percent not in DPI_PERCENTS:
            raise SystemExit(f"不支持的缩放倍率：{self.scale:g}")
        relative = DPI_PERCENTS.index(target_percent) - recommended_index
        if not self._min_relative <= relative <= self._max_relative:
            raise SystemExit(
                f"该显示不支持 {target_percent}% 缩放（允许 {self._min_relative:+d}..{self._max_relative:+d} 步）。"
            )
        if relative != self._saved_relative:
            self._set_scale(relative)

    def _get_ncm(self) -> NONCLIENTMETRICSW:
        ncm = NONCLIENTMETRICSW()
        ncm.cbSize = ctypes.sizeof(ncm)
        self._user32.SystemParametersInfoW(SPI_GETNONCLIENTMETRICS, ctypes.sizeof(ncm), ctypes.byref(ncm), 0)
        return ncm

    def _set_ncm(self, ncm: NONCLIENTMETRICSW) -> None:
        self._user32.SystemParametersInfoW(
            SPI_SETNONCLIENTMETRICS, ctypes.sizeof(ncm), ctypes.byref(ncm), SPIF_UPDATEINIFILE
        )
        _broadcast_message(self._user32, WM_SETTINGCHANGE, SPI_SETNONCLIENTMETRICS, WINDOW_METRICS)

    def _get_icon_font(self) -> LOGFONTW:
        icon = LOGFONTW()
        self._user32.SystemParametersInfoW(SPI_GETICONTITLELOGFONT, ctypes.sizeof(icon), ctypes.byref(icon), 0)
        return icon

    def _set_icon_font(self, icon: LOGFONTW) -> None:
        self._user32.SystemParametersInfoW(
            SPI_SETICONTITLELOGFONT, ctypes.sizeof(icon), ctypes.byref(icon), SPIF_UPDATEINIFILE
        )
        _broadcast_message(self._user32, WM_SETTINGCHANGE, SPI_SETICONTITLELOGFONT, None)

    def _reset_logfont(self, logfont: LOGFONTW, dpi: int) -> None:
        ctypes.memset(ctypes.byref(logfont), 0, ctypes.sizeof(logfont))
        logfont.lfHeight = -round(self.size_pt * dpi / 72)
        logfont.lfWeight = 400
        logfont.lfCharSet = 1
        logfont.lfQuality = 5
        logfont.lfFaceName = self.family

    def _apply_font(self) -> None:
        ncm = self._get_ncm()
        target_dpi = round(96 * self.scale)
        for name in ("lfCaptionFont", "lfSmCaptionFont", "lfMenuFont", "lfStatusFont", "lfMessageFont"):
            logfont = getattr(ncm, name)
            self._reset_logfont(logfont, target_dpi)
            setattr(ncm, name, logfont)

        ncm.iCaptionHeight = -ncm.lfCaptionFont.lfHeight + 10 * round(target_dpi / 96)
        if sys.getwindowsversion().build >= 22000 and ncm.iPaddedBorderWidth == 0:
            ncm.iPaddedBorderWidth = 1 + round(target_dpi / 96)

        icon = LOGFONTW()
        self._reset_logfont(icon, target_dpi)
        self._set_icon_font(icon)
        self._set_ncm(ncm)


def _root_hwnd(window: Misc) -> int:
    user32 = ctypes.WinDLL("user32")
    user32.GetAncestor.argtypes = [ctypes.c_void_p, ctypes.c_uint]
    user32.GetAncestor.restype = ctypes.c_void_p
    # Tk 的 winfo_id() 是客户区窗口，标题栏属于根窗口。
    return int(user32.GetAncestor(window.winfo_id(), GA_ROOT) or window.winfo_id())


def grab_window_windows(window: Misc) -> Image.Image:
    """用 PrintWindow 抓取含标题栏的窗口，返回不透明 RGBA。"""
    return _print_window(_root_hwnd(window)).convert("RGBA")


def _window_rects(root_hwnd: int) -> tuple[tuple[int, int, int, int], tuple[int, int, int, int]]:
    from ctypes import wintypes

    user32 = ctypes.WinDLL("user32")
    user32.GetWindowRect.argtypes = [ctypes.c_void_p, ctypes.POINTER(wintypes.RECT)]
    dwmapi = ctypes.WinDLL("dwmapi")
    dwmapi.DwmGetWindowAttribute.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_void_p, ctypes.c_uint]

    window_rect = wintypes.RECT()
    user32.GetWindowRect(root_hwnd, ctypes.byref(window_rect))
    frame_rect = wintypes.RECT()
    result = dwmapi.DwmGetWindowAttribute(
        root_hwnd, DWMWA_EXTENDED_FRAME_BOUNDS, ctypes.byref(frame_rect), ctypes.sizeof(frame_rect)
    )
    if result != 0:
        frame_rect = window_rect
    return (
        (window_rect.left, window_rect.top, window_rect.right, window_rect.bottom),
        (frame_rect.left, frame_rect.top, frame_rect.right, frame_rect.bottom),
    )


def _print_window(root_hwnd: int) -> Image.Image:
    window_rect, frame_rect = _window_rects(root_hwnd)
    width = window_rect[2] - window_rect[0]
    height = window_rect[3] - window_rect[1]
    image = _copy_window_to_image(root_hwnd, width, height)
    crop = (
        frame_rect[0] - window_rect[0],
        frame_rect[1] - window_rect[1],
        frame_rect[2] - window_rect[0],
        frame_rect[3] - window_rect[1],
    )
    return image.crop(crop)


def _copy_window_to_image(root_hwnd: int, width: int, height: int) -> Image.Image:
    from PIL import Image

    user32 = ctypes.WinDLL("user32")
    gdi32 = ctypes.WinDLL("gdi32")
    user32.GetWindowDC.argtypes = [ctypes.c_void_p]
    user32.GetWindowDC.restype = ctypes.c_void_p
    user32.ReleaseDC.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    user32.PrintWindow.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint]
    gdi32.CreateCompatibleDC.argtypes = [ctypes.c_void_p]
    gdi32.CreateCompatibleDC.restype = ctypes.c_void_p
    gdi32.CreateCompatibleBitmap.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
    gdi32.CreateCompatibleBitmap.restype = ctypes.c_void_p
    gdi32.SelectObject.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    gdi32.SelectObject.restype = ctypes.c_void_p
    gdi32.GetDIBits.argtypes = [
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_uint,
        ctypes.c_uint,
        ctypes.c_void_p,
        ctypes.POINTER(BITMAPINFO),
        ctypes.c_uint,
    ]
    gdi32.DeleteObject.argtypes = [ctypes.c_void_p]
    gdi32.DeleteDC.argtypes = [ctypes.c_void_p]

    screen_dc = user32.GetWindowDC(root_hwnd)
    mem_dc = gdi32.CreateCompatibleDC(screen_dc)
    bitmap = gdi32.CreateCompatibleBitmap(screen_dc, width, height)
    gdi32.SelectObject(mem_dc, bitmap)
    try:
        if not user32.PrintWindow(root_hwnd, mem_dc, 2):
            raise SystemExit("PrintWindow 失败。")
        bmi = BITMAPINFO()
        bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bmi.bmiHeader.biWidth = width
        bmi.bmiHeader.biHeight = -height
        bmi.bmiHeader.biPlanes = 1
        bmi.bmiHeader.biBitCount = 32
        buffer = ctypes.create_string_buffer(width * height * 4)
        if not gdi32.GetDIBits(mem_dc, bitmap, 0, height, buffer, ctypes.byref(bmi), 0):
            raise SystemExit("GetDIBits 失败。")
        return Image.frombuffer("RGBA", (width, height), buffer.raw, "raw", "BGRA", 0, 1).convert("RGB")
    finally:
        gdi32.DeleteObject(bitmap)
        gdi32.DeleteDC(mem_dc)
        user32.ReleaseDC(root_hwnd, screen_dc)
