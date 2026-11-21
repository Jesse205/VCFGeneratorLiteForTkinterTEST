"""构建截图场景并输出 PNG / WebP（亮/暗窗口后背景 + 透明）。"""

import importlib
import subprocess
import time
from contextlib import suppress
from dataclasses import dataclass, field
from pathlib import Path
from tkinter import TclError
from typing import override

from scripts.screenshot_support import (
    composite_over,
    derive_transparent,
    grab_window,
    require_executable,
    save_image,
)
from vcf_generator_lite.core.vcf_generator import InvalidItem
from vcf_generator_lite.models.contact import MissingNumberError
from vcf_generator_lite.ui.windows.invalid_items_dialog import InvalidItemsDialog
from vcf_generator_lite.ui.windows.main_window import VCFGeneratorLiteApp

MAIN_WINDOW_WIDTH_PT = 450
MAIN_WINDOW_HEIGHT_PT = 465
MAIN_WINDOW_MIN_SIZE_PT = 300
DIALOG_WIDTH_PT = 360
DIALOG_HEIGHT_PT = 320
DIALOG_MIN_SIZE_PT = 225
INVALID_ROW = 4
# Windows 参考截图把无效行的号码统一打码为 11 个星号（主窗与弹窗一致）。
INVALID_PHONE_PLACEHOLDER = "*" * 11
# ttk-text 官方示例固定取 5，而非从 TEntry padding 推导。
TEXT_PADDING = 5
# KDE Breeze 输入框为白底；maxperl ttk Breeze 默认灰底需按样式覆盖。
BREEZE_FIELD_BACKGROUND = "#fcfcfc"
BACKGROUNDS = (("light", "#ffffff"), ("dark", "#000000"))
# Windows 允许窗口大于屏幕，交给 PrintWindow 完整截图。
MAX_WINDOW_SIZE = 4000


@dataclass
class ScreenshotConfig:
    """截图场景配置，由 capture_language 在窗口创建前设置，供配置钩子读取。"""

    platform: str = "linux"
    ttk_theme: str = "clam"
    theme_dirs: list[str] = field(default_factory=list)


_config = ScreenshotConfig()


def _set_config(*, platform: str, ttk_theme: str, theme_dirs: list[str]) -> None:
    """在窗口创建前设置模块级截图配置（避免重写窗口 __init__）。"""
    global _config  # ruff: ignore[global-statement]
    _config = ScreenshotConfig(platform=platform, ttk_theme=ttk_theme, theme_dirs=theme_dirs)


class ScreenshotApp(VCFGeneratorLiteApp):
    # 不重写 __init__：所有场景覆盖都在应用规定的 _configure_ui_withdraw 钩子里完成。

    @override
    def _configure_ui_withdraw(self):
        if _config.platform == "windows":
            # 允许窗口大于 runner 屏幕，交给 PrintWindow 完整截图。
            self.wm_maxsize(MAX_WINDOW_SIZE, MAX_WINDOW_SIZE)
        elif _config.platform == "linux":
            self._load_external_themes()
            self._use_ttk_theme()
        super()._configure_ui_withdraw()
        # 示例号码为中国号段；默认按语言 territory 选规则会让 en-US 下全部行无效。
        self.selected_phone_detectors_ids = set(self.phone_detectors_ids)
        self.menu_bar.set_phone_formats_selection(True, dict.fromkeys(self.phone_detectors_ids, True))
        self.set_screenshot_size(self, MAIN_WINDOW_WIDTH_PT, MAIN_WINDOW_HEIGHT_PT, MAIN_WINDOW_MIN_SIZE_PT)
        self._replace_invalid_row()

    def _load_external_themes(self):
        # tksvg 无 cp312 wheel、仅源码构建，不作硬依赖；svg 主题需要它。
        with suppress(ImportError):
            tksvg = importlib.import_module("tksvg")
            with suppress(TclError):
                tksvg.load(self)
        for directory in _config.theme_dirs:
            base = Path(directory)
            if not base.is_dir():
                raise SystemExit(f"主题目录不存在：{base}")
            for candidate in [base, *(p for p in sorted(base.iterdir()) if p.is_dir())]:
                pkg_index = candidate / "pkgIndex.tcl"
                if not pkg_index.is_file():
                    continue
                self.tk.call("lappend", "auto_path", str(candidate))
                # pkgIndex 依赖包加载器注入的 dir 变量；动态注册（foreach）也需 source 后才可见。
                with suppress(TclError):
                    self.tk.call("set", "dir", str(candidate))
                    self.tk.call("source", str(pkg_index))
        for name in self.tk.call("package", "names"):
            if str(name).startswith("ttk::theme::"):
                with suppress(TclError):
                    self.tk.call("package", "require", name)

    def _use_ttk_theme(self):
        from tkinter import font
        from tkinter.ttk import Style

        style = Style(self)
        names = style.theme_names()
        target = next((n for n in names if n.lower() == _config.ttk_theme.lower()), None)
        if target is None:
            raise SystemExit(f"ttk 主题 {_config.ttk_theme!r} 不可用；当前：{names}")
        style.theme_use(target)
        # 部分主题用字体 spec（如 "Helvetica 10"）而非命名字体；app 的 lookup_font 按命名取，
        # 故把 spec 注册为命名字体，族取 fontconfig 已解析好的 Tk 默认族（开源字体）。
        family = font.nametofont("TkDefaultFont", root=self).cget("family")
        existing = set(font.names())
        # 命名字体随 Font 对象析构而删除，必须持有引用。
        self._spec_fonts = []
        for element in (".", "Treeview", "TButton", "TEntry", "TLabel", "Heading"):
            spec = style.lookup(element, "font")
            if not spec or spec in existing:
                continue
            parts = str(spec).split()
            size = int(parts[-1]) if parts and parts[-1].lstrip("-").isdigit() else 10
            weight = "bold" if "bold" in parts else "normal"
            self._spec_fonts.append(font.Font(root=self, name=str(spec), family=family, size=size, weight=weight))
            existing.add(str(spec))
        # ttk-text 自述文件：Text 内边距经 ThemedText.TEntry 的 textpadding 供给，固定用官方示例的 5。
        style.configure("ThemedText.TEntry", textpadding=TEXT_PADDING)
        # maxperl Breeze 的 fieldbackground 为灰色；按 KDE Breeze 在样式层覆盖为白底。
        # 必须在样式层设置，widget 级 configure 会因回退到主题 background 而重新变灰。
        if target == "Breeze":
            style.configure("ThemedText.TEntry", fieldbackground=BREEZE_FIELD_BACKGROUND)

    def set_screenshot_size(  # ruff: ignore[no-self-use]
        self, window: VCFGeneratorLiteApp | InvalidItemsDialog, width_pt: int, height_pt: int, min_pt: int
    ):
        if _config.platform == "macos":
            # Aqua 的坐标单位是点（72dpi），Retina 下再经 wm_size_pt 换算会翻倍。
            window.wm_minsize(min_pt, min_pt)
            window.wm_size(width_pt, height_pt)
        else:
            window.wm_minsize_pt(min_pt, min_pt)
            window.wm_size_pt(width_pt, height_pt)

    def _replace_invalid_row(self):
        lines = self.layout.get_text_content().split("\n")
        name = lines[INVALID_ROW - 1].split("\t")[0]
        lines[INVALID_ROW - 1] = f"{name}\t{INVALID_PHONE_PLACEHOLDER}"
        self.layout.set_text_content("\n".join(lines))
        self.layout.content_text.edit_reset()
        self.layout.content_text.edit_modified(False)
        # Linux 的光标常亮由 X 资源 *Text.insertOffTime 在窗口创建前设置；
        # macOS/Windows 无 X 资源，须在此关闭闪烁避免截到隐藏相位。
        if _config.platform != "linux":
            self.layout.content_text.configure(insertofftime=0)


def _settle(window: VCFGeneratorLiteApp | InvalidItemsDialog, seconds: float = 0.2):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        window.update()
        time.sleep(0.03)
    window.update()


def _capture_scene(
    window: VCFGeneratorLiteApp | InvalidItemsDialog,
    scene: str,
    output_dir: Path,
    lang: str,
    platform: str,
):
    if platform == "linux":
        grabs = {}
        xsetroot = require_executable("xsetroot")
        for background, color in BACKGROUNDS:
            subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true]
                [xsetroot, "-solid", color],
                check=True,
            )
            _settle(window)
            grabs[background] = grab_window(window, platform)
        images = {**grabs, "transparent": derive_transparent(grabs["light"], grabs["dark"])}
    else:
        transparent = grab_window(window, platform)
        images = {
            "transparent": transparent,
            **{background: composite_over(transparent, color) for background, color in BACKGROUNDS},
        }
    for background, image in images.items():
        save_image(image, output_dir / f"{scene}.{lang}.{background}.png")


def capture_language(
    *,
    output_dir: Path,
    platform: str,
    lang: str,
    ttk_theme: str,
    theme_dirs: list[str],
    scale: float,
    wait: float,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _set_config(platform=platform, ttk_theme=ttk_theme, theme_dirs=theme_dirs)
    app = ScreenshotApp()
    dialog = None
    try:
        app.attributes("-topmost", True)
        # WM 焦点策略不一，显式索取焦点保证插入光标可见。
        app.focus_force()
        app.layout.content_text.focus_set()
        _settle(app, wait)
        _assert_scaling(app, platform, scale)
        _assert_size(app, MAIN_WINDOW_WIDTH_PT, MAIN_WINDOW_HEIGHT_PT)
        _capture_scene(app, "main_window", output_dir, lang, platform)

        # 直接构造无效号码弹窗，不走 on_generate 的线程回调与异步轮询。
        dialog = _create_dialog(app, platform, lang)
        _assert_size(dialog, DIALOG_WIDTH_PT, DIALOG_HEIGHT_PT)
        _capture_scene(dialog, "invalid_lines_window", output_dir, lang, platform)
    finally:
        if dialog is not None:
            dialog.destroy()
        app.destroy()


def _create_dialog(app: ScreenshotApp, platform: str, lang: str) -> InvalidItemsDialog:
    filename = "我的联系人.vcf" if lang == "zh-CN" else "My Contacts.vcf"
    if platform == "windows":
        display_path = rf"C:\Users\User\Desktop\{filename}"
    elif platform == "macos":
        display_path = f"/Users/User/Desktop/{filename}"
    else:
        display_path = f"/home/user/Desktop/{filename}"
    # 弹窗原始内容直接取自主窗无效行，与 Windows 参考截图一致（同一姓名 + 同一掩码）。
    raw_content = app.layout.get_text_content().split("\n")[INVALID_ROW - 1]
    dialog = InvalidItemsDialog(
        app,
        display_path=display_path,
        invalid_items=[InvalidItem(row_position=INVALID_ROW, raw_content=raw_content, exception=MissingNumberError())],
    )
    app.set_screenshot_size(dialog, DIALOG_WIDTH_PT, DIALOG_HEIGHT_PT, DIALOG_MIN_SIZE_PT)
    dialog.attributes("-topmost", True)
    dialog.focus_force()
    _settle(dialog, 0.5)
    return dialog


def _assert_scaling(app: ScreenshotApp, platform: str, scale: float) -> None:
    actual = float(app.tk.call("tk", "scaling"))
    # X11 以 96dpi 为 1x；Windows 的系统缩放通过 WindowsSystemSettings 设置，Tk scaling 期望 scale。
    expected = 96 / 72 * scale if platform == "linux" else scale
    print(f"[{platform}] tk scaling={actual:.3f}（期望 {expected:.3f}）", flush=True)
    if abs(actual - expected) > expected * 0.03:
        raise SystemExit(
            f"缩放未生效：tk scaling={actual:.3f}，期望 {expected:.3f}。"
            "Linux 请检查 Xvfb -dpi 与 Xft.dpi；macOS 请确认 HiDPI；Windows 请检查系统缩放覆盖。"
        )


def _assert_size(window: ScreenshotApp | InvalidItemsDialog, width_pt: int, height_pt: int) -> None:
    expected_width = window.winfo_pixels(f"{width_pt}p")
    expected_height = window.winfo_pixels(f"{height_pt}p")
    if window.winfo_width() + 2 < expected_width or window.winfo_height() + 2 < expected_height:
        raise SystemExit(
            f"窗口被裁剪：{window.winfo_width()}x{window.winfo_height()}，"
            f"期望 {expected_width}x{expected_height}。请提高 runner 分辨率。"
        )
